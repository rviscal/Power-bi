import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import google.generativeai as genai

# 1. Configuração do Gemini (USE O MODELO 1.5)
# AVISO: Gere uma nova chave, a sua anterior vazou!
os.environ["GEMINI_API_KEY"] = "COLE_SUA_NOVA_CHAVE_AQUI" 
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# CORREÇÃO: O modelo correto é 'gemini-1.5-flash' ou 'gemini-1.5-pro'
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Configuração do Servidor Power BI
server_params = StdioServerParameters(
    command="C:\\Users\\rodol\\.vscode\\extensions\\analysis-services.powerbi-modeling-mcp-0.1.9-win32-x64\\server\\powerbi-modeling-mcp.exe",
    args=["--start", "--skip-confirmation"],
    env=None
)

async def run_chat():
    print("Iniciando conexão com Power BI...")
    
    # Conecta ao servidor MCP do Power BI
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # Inicializa a sessão
            await session.initialize()
            
            # Lista as ferramentas disponíveis no Power BI
            tools = await session.list_tools()
            tool_names = [t.name for t in tools.tools]
            print(f"\n🔌 Conectado ao Power BI! {len(tool_names)} ferramentas carregadas.")
            print(f"🛠️ Exemplo de ferramentas: {tool_names[:5]}...")
            
            # Histórico do chat para manter contexto
            chat = model.start_chat(history=[])

            while True:
                user_input = input("\nVocê (Gemini + PBI): ")
                if user_input.lower() in ["sair", "exit"]:
                    break

                # Contexto enriquecido para o Gemini saber o que ele pode fazer
                prompt_sistema = f"""
                Você é um assistente especialista em Power BI conectado via MCP.
                O usuário tem um relatório aberto.
                
                FERRAMENTAS DISPONÍVEIS NO SISTEMA (Você não pode executá-las diretamente neste script simples, mas deve sugerir o uso delas):
                {tool_names}
                
                PERGUNTA DO USUÁRIO:
                {user_input}
                
                Se o usuário pedir código DAX, gere o código.
                Se o usuário perguntar sobre a estrutura, explique que você vê as ferramentas mas precisa de permissão de execução (nesta versão do script).
                """
                
                try:
                    response = chat.send_message(prompt_sistema)
                    print(f"\nGemini: {response.text}")
                except Exception as e:
                    print(f"Erro na API do Gemini: {e}")

if __name__ == "__main__":
    asyncio.run(run_chat())