

def chat(context: 'micro_context', message: str):
    ''' will broadcast message to all clients '''

    context.broadcast("said", {
        "message": message,
        "client": context.client_id
    })
