from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from texts import message_list
from states import ChooseState
from aiogram.fsm.context import FSMContext
import kb
router = Router()
from sqlrequests import insert_info, drop_table, get_col_by_col

from main import bot

@router.message(Command("start"))
async def start_handler(msg: Message):
    # await drop_table('users')
    # await drop_table('twitchers')
    await msg.delete()
    await msg.answer(message_list['start'], reply_markup=kb.menu) #message_list['start']

@router.message(ChooseState())
async def message_handler(msg: Message, state: FSMContext):
    cur_state = await state.get_state()
    if cur_state == 'ChooseState:waiting_for_channel':
        try:
            admins = await bot.get_chat_administrators(msg.text)
            admins = [a.user.id for a in admins]

            if msg.from_user.id in admins:
                await msg.answer(text=message_list['getting_chanel']['chanel_added'])
                await insert_info('users', [msg.chat.id, msg.text])
                await msg.answer(text=message_list['getting_chanel']['next_step'])
                await state.set_state(state=ChooseState.waiting_for_twitch)
            else:
                await msg.answer(text=f'{msg.from_user.username}{message_list["getting_chanel"]["error_message"]}')
            
        except Exception as e:
            await msg.answer(f"Такого канала не существует или вы еще не добавили бота в канал. { e }")

    elif cur_state == 'ChooseState:waiting_for_twitch':
        user_id = await get_col_by_col('users', 'id', 'tg_id', msg.chat.id)
        await insert_info('twitchers', [user_id, msg.text])
        await msg.answer(text=message_list['getting_twitch']['twitch_added'])
        await state.set_state(state=ChooseState.null)
        
@router.callback_query(lambda call: True)
async def call_back_handler(call: CallbackQuery, state: FSMContext):
    if call.data == 'ch;channel':
        tg_id = await get_col_by_col('users', 'tg_id', 'tg_id', call.message.chat.id)
        if not tg_id:
            await state.set_state(state=ChooseState.waiting_for_channel)
            await call.message.answer(f'Введите название своего канала.')
        else:
            # Надо сделать кнопку редактирования канала и добавления twitch
            await call.message.answer("Вы уже указали канал.")

