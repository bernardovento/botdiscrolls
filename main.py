import discord
import requests
import json
from privateinfos import *

from discord import app_commands

def separar_string(res):
    import re
    res = res.replace(" ", "")  # Remove espaços
    pattern = r"(?:\d+)?d\d+(?:[kl]\d+)?(?:[*/+-]\d+)?"
    matches = re.findall(pattern, res)
    print(f"Separar string: {matches}")  # Debug print
    return matches

def parse_roll(roll):
    import re
    pattern = r"(\d+)?d(\d+)([kl]\d+)?([*/+-]\d+)?"
    match = re.match(pattern, roll)
    if match:
        quantidade = int(match.group(1)) if match.group(1) else 1
        lados = int(match.group(2))
        adv = match.group(3) if match.group(3) else ""
        mod = match.group(4) if match.group(4) else ""
        
        adv_type = adv[0] if adv else None
        adv_num = int(adv[1:]) if adv else 0
        
        mod_type = mod[0] if mod else None
        mod_num = int(mod[1:]) if mod else 0

        print(f"Parse roll - quantidade: {quantidade}, lados: {lados}, adv_type: {adv_type}, adv_num: {adv_num}, mod_type: {mod_type}, mod_num: {mod_num}")  # Debug print
        return quantidade, lados, adv_type, adv_num, mod_type, mod_num
    return 0, 0, None, 0, None, 0

def RawData(dices, sides):
    raw_data = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": apiKey,
            "n": dices,
            "min": 1,
            "max": sides,
            "replacement": True
        },
        'id': 1
    }
    return raw_data

headers = {
    'Content-type': 'application/json',
    'Accept': 'application/json'
}

class client(discord.Client):

    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(intents=intents)
        self.synced = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:
            await tree.sync(guild=discord.Object(id=id_do_servidor))
            self.synced = True
        print(f"Entramos como {self.user}.")

aclient = client()
tree = app_commands.CommandTree(aclient)

@tree.command(
    guild=discord.Object(id=id_do_servidor),
    name='r',
    description='Comando para rolar dados com aleatoriedade real "/r <quantidade>d<lado> <modificadores>"')
async def slash2(interaction: discord.Interaction, dice: str=None):
    if dice is None:
        await interaction.response.send_message("Por favor, forneça a rolagem dos dados.")
        return
    
    rolls = separar_string(dice)
    print(f"Rolls: {rolls}")  # Debug print
    total_result = 0
    all_results = []
    formatted_results = []

    for roll in rolls:
        quantidade, lados, adv_type, adv_num, mod_type, mod_num = parse_roll(roll)
        
        data = json.dumps(RawData(quantidade, lados))
        response = requests.post(url='https://api.random.org/json-rpc/2/invoke', data=data, headers=headers)
        json_data = json.loads(response.text)

        if 'result' not in json_data:
            print(f"Erro na resposta da API: {json_data}")  # Debug print
            await interaction.response.send_message("Erro ao acessar a API de rolagem de dados. Por favor, tente novamente.")
            return

        resultados = json_data['result']['random']['data']
        print(f"Resultados: {resultados}")  # Debug print

        formatted_roll = []
        if adv_type == 'k':  # Keep highest
            kept = sorted(resultados, reverse=True)[:adv_num]
            discarded = sorted(resultados, reverse=True)[adv_num:]
        elif adv_type == 'l':  # Keep lowest
            kept = sorted(resultados)[:adv_num]
            discarded = sorted(resultados)[adv_num:]
        else:
            kept = resultados
            discarded = []

        for r in resultados:
            if r in kept:
                formatted_roll.append(f"**{r}**")
                kept.remove(r)
            else:
                formatted_roll.append(str(r))
        
        formatted_results.append(" ".join(formatted_roll))
        resultado = sum(int(r.strip("**")) if r.startswith("**") and r.endswith("**") else int(r) for r in formatted_roll)
        print(f"Resultado antes do modificador: {resultado}")  # Debug print

        if mod_type == '+':
            resultado += mod_num
        elif mod_type == '-':
            resultado -= mod_num
        elif mod_type == '*':
            resultado *= mod_num
        elif mod_type == '/':
            resultado /= mod_num

        print(f"Resultado após o modificador: {resultado}")  # Debug print
        total_result += resultado
        all_results.append(resultados)

    formatted_message = "\n".join(formatted_results)
    await interaction.response.send_message(
        f"Rolagem {dice} com resultado:\n{formatted_message}\nCom a soma total {total_result}")

aclient.run(tokendisc)