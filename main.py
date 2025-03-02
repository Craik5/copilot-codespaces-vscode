from .. import loader, utils
import asyncio
import logging
import hikkatl

logger = logging.getLogger(__name__)

def register(cb):
    cb(CraikMod())

class CraikMod(loader.Module):
    """🤖 Модуль ИИ @IceFloeBot — отвечает на вопросы через команду .craik"""
    strings = {'name': 'Craik AI'}

    def __init__(self):
        self.config = loader.ModuleConfig("craik_mode", False, "⚙️ Включен ли режим Craik?")
        self.queue = asyncio.Queue()
        self.processing = False

    async def craik3cmd(self, message):
        """⚙️ Включить/выключить режим Craik.
        
        📌 Использование: .craik ваш вопрос
        """
        self.config['craik_mode'] = not self.config['craik_mode']
        status = "✅ включен" if self.config['craik_mode'] else "❌ выключен"
        await message.edit(f"⚙️ Режим Craik {status}!")

    async def craikcmd(self, message):
        """🤖 Задать вопрос нейросети.
        
        📌 Использование: .craik ваш вопрос
        """
        if not self.config['craik_mode']:
            return
        
        question = message.raw_text[len(".craik"):].strip()
        
        if not question:
            await message.edit("⚠️ После команды .craik напишите вопрос!")
            return
        
        await self.queue.put((message, question))
        if not self.processing:
            self.processing = True
            await self.process_queue()

    async def process_queue(self):
        while not self.queue.empty():
            message, question = await self.queue.get()
            
            await message.edit("💭 Думаю...")
            
            async with message.client.conversation("@IceFloeBot") as conv:
                prompt = f"Ответь на вопрос коротко: {question}"
                msg = await conv.send_message(prompt)
                response1 = await conv.get_response()
                
                while "думаю" in response1.text.lower():
                    response1 = await conv.get_response()
                
                response_text = f"👤 Вопрос: {question}\n\n🤖 Craik X: {response1.text}"
                await message.edit(response_text)
                await msg.delete()
                await response1.delete()
            
            await asyncio.sleep(11)  # Ожидание перед следующим запросом
        
        self.processing = False
