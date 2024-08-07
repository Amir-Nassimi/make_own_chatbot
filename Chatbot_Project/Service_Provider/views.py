import requests
from pathlib import Path
import os, sys, yaml, subprocess, psutil

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import TrainableData, ChatBot
from .serializers import TrainableDataSerializer, ChatBotSerializer

sys.path.append(os.path.abspath(Path(__file__).resolve().parents[1]))
from conf import Config



class TrainableDataViewSet(ModelViewSet):
    queryset = TrainableData.objects.all()
    serializer_class = TrainableDataSerializer
    permission_classes = [IsAuthenticated]


class ChatBotViewSet(ModelViewSet):
    queryset = ChatBot.objects.all()
    serializer_class = ChatBotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatBot.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data['user'] = request.user.id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProvideServiceViewSet(ViewSet):
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def train(self, request, pk=None):
        try:
            bot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist as error:
            return Response(f'This ChatBot is not exists or the info is not valid:{error}.', status=status.HTTP_404_NOT_FOUND)

        data_list = TrainableData.objects.filter(bot=bot)
        
        nlu_data = {'version': '3.1', 'nlu': []}
        stories_data = {'version': '3.1', 'stories': []}
        domain_data = {'version': '3.1', 'intents': [], 'responses': {}}
    
        if data_list.exists():
            for data in data_list:
                nlu_data['nlu'].append({
                    'intent': data.topic,
                    'examples': '\n'.join([f'- {example}' for example in data.questions.split(', ')])
                })

                domain_data['intents'].append(data.topic)
                domain_data['responses'][f'utter_{data.topic}'] = [
                    {'text': response} for response in data.answers.split(', ')
                ]

                stories_data['stories'].append({
                    'story': f'{data.topic} story',
                    'steps': [
                        {'intent': data.topic},
                        {'action': f'utter_{data.topic}'}
                    ]
                })
        else:
            return Response(f'The respected bot has no trained data modified for it!!', status=status.HTTP_400_BAD_REQUEST)

        models_path = os.path.join(Config().Path(bot.id), 'models')
        config_path = os.path.join(Config().Path(bot.id), 'config.yml')
        nlu_file_path = os.path.join(Config().Path(bot.id), f'nlu_{bot.id}.yml')
        domain_file_path = os.path.join(Config().Path(bot.id), f'domain_{bot.id}.yml')
        stories_file_path = os.path.join(Config().Path(bot.id), f'stories_{bot.id}.yml')

        os.makedirs(models_path, exist_ok=True)
        os.makedirs(Config().Path(bot.id), exist_ok=True)

        with open(nlu_file_path, 'w') as nlu_file:
            nlu_file.write(f"version: '3.1'\nnlu:\n")
            for item in nlu_data['nlu']:
                nlu_file.write(f"- intent: {item['intent']}\n  examples: |\n")
                for line in item['examples'].split('\n'):
                    nlu_file.write(f"    {line}\n")

        with open(domain_file_path, 'w') as domain_file:
            yaml.dump(domain_data, domain_file, default_flow_style=False)
        
        with open(stories_file_path, 'w') as stories_file:
            yaml.dump(stories_data, stories_file, default_flow_style=False)

        try:
            subprocess.run([
                'rasa', 'train', '--domain', domain_file_path, '--data', nlu_file_path, stories_file_path,
                '--out', models_path, '--config', config_path
            ], check=True)

        except subprocess.CalledProcessError as error:
            return Response(f'Called-Process Error on Subprocess: {error}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as error:
            return Response(f'Error on Subprocess: {error}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            try:
                os.remove(nlu_file_path)
                os.remove(domain_file_path)
                os.remove(stories_file_path)
            except Exception as error:
                return Response(f'Failed to clean up training data files: {error}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response('This ChatBot has been trained sucesfully!', status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def initialize(self, request, pk=None):
        try:
            bot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist as error:
            return Response(f'This ChatBot is not exists or the info is not valid:{error}.', status=status.HTTP_404_NOT_FOUND)
        
        if bot.is_active:
            return Response('This ChatBot has been initialized before!', status=status.HTTP_200_OK)

        model_path = os.path.join(Config().Path(bot.id), 'models')

        if os.path.exists(model_path):
            port = 8001

            conda_activate_cmd = "conda run -n MakeOwnChatbot"
            rasa_cmd = f"rasa run --model {model_path} --port {port} --enable-api"
            full_cmd = f"{conda_activate_cmd} {rasa_cmd}"

            try:
                process = subprocess.Popen(full_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                bot.PORT = 8001
                bot.IP = 'localhost'
                bot.PID = process.pid
                bot.is_active = True
                bot.save()
                return Response('This ChatBot has been initialized sucesfully!', status=status.HTTP_200_OK)
            except Exception as error:
                return Response(f'Failed to start ChatBot: {error}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response("No chatbot found!", status=status.HTTP_404_NOT_FOUND)


    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def stop(self, request, pk=None):
        try:
            bot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist as error:
            return Response(f'This ChatBot is not exists or the info is not valid:{error}.', status=status.HTTP_404_NOT_FOUND)

        if not bot.is_active:
            return Response('This ChatBot has not been initialized yet!', status=status.HTTP_200_OK)

        if psutil.pid_exists(bot.PID):
            process = psutil.Process(bot.PID)
            try:
                for child in process.children(recursive=True):
                    child.kill()
                process.terminate()

                if psutil.pid_exists(bot.PID):
                    process.kill()
                
            except psutil.NoSuchProcess:
                return Response('This ChatBot has already been terminated!', status=status.HTTP_200_OK)
        else:
            return Response('Process not found', status=status.HTTP_404_NOT_FOUND)
        
        bot.PID = None
        bot.is_active = False
        bot.save()
        return Response('This ChatBot has been terminated sucesfully!', status=status.HTTP_200_OK)
    

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def message(self, request, pk=None):
        try:
            bot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist as error:
            return Response(f'This ChatBot is not exists or the info is not valid:{error}.', status=status.HTTP_404_NOT_FOUND)

        if not bot.is_active:
            return Response('This ChatBot has not been initialized yet!', status=status.HTTP_200_OK)

        message = request.data.get('message', None)

        if not message:
            return Response("No message provided", status=status.HTTP_400_BAD_REQUEST)
        
        rasa_url = f"http://{bot.IP}:{bot.PORT}/webhooks/rest/webhook"

        try:
            response = requests.post(rasa_url, json={"message": message})
        except requests.RequestException as error:
            return Response(f'Failed to interact with Rasa server: {error}', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(response.json(), status=response.status_code)


    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def resource_usage(self, request, pk=None):
        try:
            chatbot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist:
            return Response({"error": "Chatbot not found"}, status=status.HTTP_404_NOT_FOUND)

        if not chatbot.PID:
            return Response({"error": "Chatbot is not running"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # Get the parent process using psutil
            parent_process = psutil.Process(chatbot.PID)

            # Initialize cumulative resource usage variables
            total_memory_rss = 0
            total_memory_vms = 0
            total_cpu_usage = 0

            # List to keep track of all processes (parent + children)
            processes = [parent_process] + parent_process.children(recursive=True)

            for process in processes:
                memory_info = process.memory_info()
                total_memory_rss += memory_info.rss  # Resident Set Size
                total_memory_vms += memory_info.vms  # Virtual Memory Size
                total_cpu_usage += process.cpu_percent(interval=1.0)

            resource_usage = {
                "memory_rss": total_memory_rss,
                "memory_vms": total_memory_vms,
                "memory_percent": parent_process.memory_percent(),  # Memory usage percentage
                "cpu_usage_percent": total_cpu_usage  # CPU usage percentage
            }

            return Response(resource_usage, status=status.HTTP_200_OK)
        except psutil.NoSuchProcess:
            return Response("Process does not exist", status=status.HTTP_404_NOT_FOUND)
        except Exception as error:
            return Response("Failed to retrieve resource usage", status=status.HTTP_500_INTERNAL_SERVER_ERROR)
