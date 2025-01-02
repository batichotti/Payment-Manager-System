from config import supabase
from models.client import Client

class ClientService:
    @staticmethod
    def get_client_by_id(client_id):
        response = supabase.table("clients").select("*").eq("id", client_id).execute()
        if response.data:
            return Client.from_dict(response.data[0])
        return None
