import discord
import requests
import json
from  privateinfos import *

from discord import app_commands

def RawData(dices, sides):
    raw_data = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",  #random numbers will be integers
        "params": {
            "apiKey": apiKey,
            "n": dices,  # how many random numbers to generate
            "min": 1,  # min and max for the random integers, inclusive
            "max": sides,
            "replacement": True
        },
        'id': 1
    }
    return raw_data



headers = {
    'Content-type': 'application/json',
    'Content-Length': '200',
    'Accept': 'application/json'
}

class client(discord.Client):

  def __init__(self):
    super().__init__(intents=discord.Intents.default())
    self.synced = False  #Nós usamos isso para o bot não sincronizar os comandos mais de uma vez

  async def on_ready(self):
    await self.wait_until_ready()
    if not self.synced:  #Checar se os comandos slash foram sincronizados
      await tree.sync(
          guild=discord.Object(id=id_do_servidor)
      )  # Você também pode deixar o id do servidor em branco para aplicar em todos servidores, mas isso fará com que demore de 1~24 horas para funcionar.
      self.synced = True
    print(f"Entramos como {self.user}.")


aclient = client()
tree = app_commands.CommandTree(aclient)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


#Comando usando /d2
@tree.command(
    guild=discord.Object(id=id_do_servidor),
    name='r',
    description='Rolando um d2')  #Comando específico para seu servidor
async def slash2(interaction: discord.Interaction, dice: str=None):
    if dice == None:
        return
    try:
        diceNumbers = dice.split('d')[0]
        if diceNumbers == '':
            diceNumbers = '1'
        diceSides = dice.split('d')[1]
        data = json.dumps(RawData(diceNumbers, diceSides))
        response = requests.post(url='https://api.random.org/json-rpc/2/invoke',      
                            data=data,
                            headers=headers)
        json_data = json.loads(response.text)
        await interaction.response.send_message(
            f"Resultado: Rolagem {dice} com resultado {json_data['result']['random']['data']}, com a soma total {sum(json_data['result']['random']['data'])}", ephemeral=True)
    except:
        await interaction.response.send_message(
            f"Não entendi a rolagem!", ephemeral=True)

#Fim do /d2

#Chave discord
aclient.run(
    tokendisc)