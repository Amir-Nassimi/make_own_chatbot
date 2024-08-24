import os
import subprocess
import sys
from pathlib import Path
from uuid import UUID

import psutil
import requests
import yaml
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from .models import ChatBot, TrainableData, QuestionsData
from .serializers import ChatBotSerializer, TrainableDataSerializer

sys.path.append(os.path.abspath(Path(__file__).resolve().parents[1]))
from conf import Config


class TrainableDataViewSet(ModelViewSet):
    queryset = TrainableData.objects.all()
    serializer_class = TrainableDataSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            ChatBot.objects.get(
                id=UUID(request.data["bot"]),
                user=request.user,
                is_trained=False,
                is_active=False,
            )
        except KeyError:
            pass
        except ChatBot.DoesNotExist:
            return Response(
                "This Chatbot has already been trained!!",
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatBotViewSet(ModelViewSet):
    queryset = ChatBot.objects.all()
    serializer_class = ChatBotSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatBot.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        request.data["user"] = request.user.id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED, headers=headers
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProvideServiceViewSet(ViewSet):
    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def train(self, request, pk=None):
        try:
            bot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist as error:
            return Response(
                f"This ChatBot is not exists or the info is not valid:{error}.",
                status=status.HTTP_404_NOT_FOUND,
            )

        data_list = TrainableData.objects.filter(bot=bot)

        nlu_data = {"version": "3.1", "nlu": []}
        stories_data = {"version": "3.1", "stories": []}
        domain_data = {"version": "3.1", "intents": [], "responses": {}}

        if data_list.exists():
            for data in data_list:
                questions_list = QuestionsData.objects.filter(trainable=data) 
                
                if not questions_list.exists():
                    return Response(
                        f"This ChatBot has no valid questions!!",
                        status=status.HTTP_404_NOT_FOUND,
                    )

                nlu_data["nlu"].append(
                    {
                        "intent": data.topic,
                        "examples": "\n".join(
                            [f"- {example.question}" for example in questions_list]
                        ),
                    }
                )

                domain_data["intents"].append(data.topic)
                domain_data["responses"][f"utter_{data.topic}"] = [
                    {"text": response} for response in data.answers.split(", ")
                ]

                stories_data["stories"].append(
                    {
                        "story": f"{data.topic} story",
                        "steps": [
                            {"intent": data.topic},
                            {"action": f"utter_{data.topic}"},
                        ],
                    }
                )
        else:
            return Response(
                f"The respected bot has no trained data modified for it!!",
                status=status.HTTP_400_BAD_REQUEST,
            )

        models_path = os.path.join(Config().Path(bot.id), "models")

        base_dir = f"{os.path.abspath(Path(__file__).resolve().parents[2])}/LLM_Service"
        nlu_file_path = os.path.join(base_dir, f"nlu_{bot.id}.yml")
        domain_file_path = os.path.join(base_dir, f"domain_{bot.id}.yml")
        stories_file_path = os.path.join(base_dir, f"stories_{bot.id}.yml")

        os.makedirs(models_path, exist_ok=True)
        os.makedirs(Config().Path(bot.id), exist_ok=True)

        with open(nlu_file_path, "w") as nlu_file:
            nlu_file.write(f"version: '3.1'\nnlu:\n")
            for item in nlu_data["nlu"]:
                nlu_file.write(f"- intent: {item['intent']}\n  examples: |\n")
                for line in item["examples"].split("\n"):
                    nlu_file.write(f"    {line}\n")

        with open(domain_file_path, "w") as domain_file:
            yaml.dump(domain_data, domain_file, default_flow_style=False)

        with open(stories_file_path, "w") as stories_file:
            yaml.dump(stories_data, stories_file, default_flow_style=False)

        try:
            target_directory = f"{os.path.abspath(Path(__file__).resolve().parents[1])}/RasaData/{bot.id}"

            subprocess.run(
                [
                    "rasa",
                    "train",
                    "--domain",
                    f"domain_{bot.id}.yml",
                    "--data",
                    f"nlu_{bot.id}.yml",
                    f"stories_{bot.id}.yml",
                    "--out",
                    f"{target_directory}/models",
                    "--config",
                    f"{base_dir}/config.yml",
                ],
                check=True,
                shell=False,
                cwd=base_dir,
            )

        except subprocess.CalledProcessError as error:
            return Response(
                f"Called-Process Error on Subprocess: {error}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as error:
            return Response(
                f"Error on Subprocess: {error}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            os.remove(nlu_file_path)
            os.remove(domain_file_path)
            os.remove(stories_file_path)
        except Exception as error:
            return Response(
                f"Failed to clean up training data files: {error}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        bot.is_trained = True
        bot.save()
        return Response(
            "This ChatBot has been trained sucesfully!", status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def initialize(self, request, pk=None):
        try:
            bot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist as error:
            return Response(
                f"This ChatBot is not exists or the info is not valid:{error}.",
                status=status.HTTP_404_NOT_FOUND,
            )

        if bot.is_active:
            return Response(
                "This ChatBot has been initialized before!", status=status.HTTP_200_OK
            )

        target_directory = (
            f"{os.path.abspath(Path(__file__).resolve().parents[2])}/LLM_Service"
        )
        model_path = f"{os.path.abspath(Path(__file__).resolve().parents[1])}/RasaData/{bot.id}/models"

        if os.path.exists(model_path):
            port = 8001

            conda_activate_cmd = "conda run -n MakeOwnChatbot"
            rasa_cmd = f"rasa run --model {model_path} --port {port} --enable-api"
            full_cmd = f"{conda_activate_cmd} {rasa_cmd}"

            try:
                process = subprocess.Popen(
                    full_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=target_directory,
                )

                bot.PORT = 8001
                bot.IP = "localhost"
                bot.PID = process.pid
                bot.is_active = True
                bot.save()
                return Response(
                    "This ChatBot has been initialized sucesfully!",
                    status=status.HTTP_200_OK,
                )
            except Exception as error:
                return Response(
                    f"Failed to start ChatBot: {error}",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        else:
            return Response("No chatbot found!", status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def stop(self, request, pk=None):
        try:
            bot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist as error:
            return Response(
                f"This ChatBot is not exists or the info is not valid:{error}.",
                status=status.HTTP_404_NOT_FOUND,
            )

        if not bot.is_active:
            return Response(
                "This ChatBot has not been initialized yet!", status=status.HTTP_200_OK
            )

        if psutil.pid_exists(bot.PID):
            process = psutil.Process(bot.PID)
            try:
                for child in process.children(recursive=True):
                    child.kill()
                process.terminate()

                if psutil.pid_exists(bot.PID):
                    process.kill()

            except psutil.NoSuchProcess:
                return Response(
                    "This ChatBot has already been terminated!",
                    status=status.HTTP_200_OK,
                )
        else:
            return Response("Process not found", status=status.HTTP_404_NOT_FOUND)

        bot.PID = None
        bot.is_active = False
        bot.save()
        return Response(
            "This ChatBot has been terminated sucesfully!", status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], permission_classes=[IsAuthenticated])
    def message(self, request, pk=None):
        try:
            bot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist as error:
            return Response(
                f"This ChatBot is not exists or the info is not valid:{error}.",
                status=status.HTTP_404_NOT_FOUND,
            )

        if not bot.is_active:
            return Response(
                "This ChatBot has not been initialized yet!", status=status.HTTP_200_OK
            )

        message = request.data.get("message", None)

        if not message:
            return Response("No message provided", status=status.HTTP_400_BAD_REQUEST)

        rasa_url = f"http://{bot.IP}:{bot.PORT}/webhooks/rest/webhook"

        try:
            response = requests.post(rasa_url, json={"message": message})
            print(response)
        except requests.RequestException as error:
            return Response(
                f"Failed to interact with Rasa server: {error}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        return Response(response.json(), status=response.status_code)

    @action(detail=True, methods=["get"], permission_classes=[IsAuthenticated])
    def resource_usage(self, request, pk=None):
        def format_memory_size(size_in_bytes):
            # Convert bytes to a human-readable format
            for unit in ["B", "KB", "MB", "GB", "TB"]:
                if size_in_bytes < 1024:
                    return f"{size_in_bytes:.2f} {unit}"
                size_in_bytes /= 1024

        try:
            chatbot = ChatBot.objects.get(user=request.user, id=pk)
        except ChatBot.DoesNotExist:
            return Response(
                {"error": "Chatbot not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if not chatbot.PID:
            return Response(
                {"error": "Chatbot is not running"}, status=status.HTTP_404_NOT_FOUND
            )

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
                "memory_rss": format_memory_size(total_memory_rss),
                "memory_vms": format_memory_size(total_memory_vms),
                "memory_percent": f"{parent_process.memory_percent():.2f}%",
                "cpu_usage_percent": f"{total_cpu_usage:.2f}%",
            }

            return Response(resource_usage, status=status.HTTP_200_OK)
        except psutil.NoSuchProcess as error:
            return Response(
                f"Process does not exist: {error}", status=status.HTTP_404_NOT_FOUND
            )
        except Exception as error:
            return Response(
                f"Failed to retrieve resource usage: {error}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
