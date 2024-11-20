class Messages:
    def __init__(self) -> None:
        pass

    def get_messages():
        """Esta função é responsável por recuperar as mensagens da API e processá-las."""

        # Check if exists messages to be retrieved

        # # Get the authentication token
        # auth_service = AuthenticationService()
        # token = auth_service.login(settings.API_USER, settings.API_PASSWORD)

        # if token:
        #     # Get the message list
        #     message_list = MessageProcessorService(token).get_messages()

        #     if len(message_list['Errors']) == 0:
        #         # Download the messages
        #         download = DownloadMessages(
        #             settings.SERVER_BASE_ADDRESS, token['headers'], message_list['Messages']
        #         )
        #         messages = download.download_messages()

        #         # Marking the message as processed
        #         for message in messages:
        #             processed = MessageProcessorService(token).mark_as_processed(  # noqa: F841
        #                 message['ResultData']
        #             )

        #         # Logout from API
        #         auth_service.logout(token['Token'])

        #         # Process the downloaded messages
        #         if len(messages) != 0:
        #             file_handler.create_message_files(messages)

        ...
