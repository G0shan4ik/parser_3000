from asyncio import get_event_loop

from aiogram.types import CallbackQuery, FSInputFile
from aiogram.utils.markdown import hbold

import time

from .helpers import FlagsManager, formatted_info_text, del_unnecessary_info, FlagKey, PARSING_LIST_TEXT
from .core import router, bott, ADMIN
from .keyboard import info_kb, main_kb, single_parsers_kb, cancel_kb
from p3000.parsers.pars_manager import VladimirManager, IvanovoManager, AllParsManager

from p3000.parsers import start_pars


# Parsing handlers
@router.callback_query(lambda query: query.data.startswith('vladimir'))
async def return_calculate_menu(query: CallbackQuery):
    flag = FlagsManager()
    if (await flag.read_flag_value('vladimir', "bool") and
        await flag.read_flag_value('vladimir', "state") != "completed!"):
        await query.answer(
            text='Parser VLADIMIR already exists!',
            show_alert=True
        )
        return

    await query.answer(
        text='Success Start pars VLADIMIR',
        show_alert=True
    )

    await flag.update_full_flag(
        'vladimir',
        {
            "bool": True,
            "minutes": 0,
            "seconds": 0,
            "state": "in process",
            "errors": await flag.read_flag_value('vladimir', "errors")
        }
    )

    start_time = time.time()

    vladimir = VladimirManager()
    exel: str = await vladimir.run_vladimir_module()

    minutes = int(int(time.time() - start_time) / 60)
    seconds = int(time.time() - start_time) % 60

    await flag.update_full_flag(
        'vladimir',
        {
            "bool": False,
            "minutes": minutes,
            "seconds": seconds,
            "state": "completed!",
            "errors": await flag.read_flag_value('vladimir', "errors")
        }
    )
    await bott.send_document(
        chat_id=query.message.chat.id,
        document=FSInputFile(f'{exel}')
    )

@router.callback_query(lambda query: query.data.startswith('ivan'))
async def return_calculate_menu(query: CallbackQuery):
    flag = FlagsManager()
    if (await flag.read_flag_value('ivan', "bool") and
        await flag.read_flag_value('ivan', "state") != "completed!"):
        await query.answer(
            text='Parser IVANOVO already exists!',
            show_alert=True
        )
        return

    await query.answer(
        text='Success Start pars IVANOVO',
        show_alert=True
    )

    await flag.update_full_flag(
        'ivan',
        {
            "bool": True,
            "minutes": 0,
            "seconds": 0,
            "state": "in process",
            "errors": await flag.read_flag_value('ivan', "errors")
        }
    )

    start_time = time.time()

    ivan = IvanovoManager()
    exel: str = await ivan.run_ivanovo_module()

    minutes = int(int(time.time() - start_time) / 60)
    seconds = int(time.time() - start_time) % 60

    await flag.update_full_flag(
        'ivan',
        {
            "bool": False,
            "minutes": minutes,
            "seconds": seconds,
            "state": "completed!",
            "errors": await flag.read_flag_value('ivan', "errors")
        }
    )

    await bott.send_document(
        chat_id=query.message.chat.id,
        document=FSInputFile(f'{exel}')
    )

@router.callback_query(lambda query: query.data.startswith('pars_all'))
async def return_calculate_menu(query: CallbackQuery):
    flag = FlagsManager()
    if (await flag.read_flag_value('all_pars', "bool") and
            await flag.read_flag_value('all_pars', "state") != "completed!"):
        await query.answer(
            text='Parser ALL_OBJECTS already exists!',
            show_alert=True
        )
        return

    await query.answer(
        text='Success Start pars ALL_OBJECTS',
        show_alert=True
    )

    await flag.update_full_flag(
        'all_pars',
        {
            "bool": True,
            "minutes": 0,
            "seconds": 0,
            "state": "in process",
            "errors": await flag.read_flag_value('all_pars', "errors")
        }
    )

    start_time = time.time()

    all_pars = AllParsManager()
    exel: str = await all_pars.run_all_parsers_module()

    minutes = int(int(time.time() - start_time) / 60)
    seconds = int(time.time() - start_time) % 60

    await flag.update_full_flag(
        'all_pars',
        {
            "bool": False,
            "minutes": minutes,
            "seconds": seconds,
            "state": "completed!",
            "errors": await flag.read_flag_value('all_pars', "errors")
        }
    )
    await bott.send_document(
        chat_id=query.message.chat.id,
        document=FSInputFile(f'{exel}')
    )



@router.callback_query(lambda query: query.data.startswith('single'))
async def return_calculate_menu(query: CallbackQuery):
    await bott.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )
    await bott.send_message(
        text='Select the name of the parser...',
        chat_id=query.message.chat.id,
        reply_markup=single_parsers_kb()
    )

@router.callback_query(lambda query: query.data.startswith('_single'))
async def return_calculate_menu(query: CallbackQuery):
    await bott.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )

    name_parser: FlagKey = query.data.split('#')[-1]

    flag = FlagsManager()
    await flag.add_flag(name_parser)

    if (await flag.read_flag_value(name_parser, "bool") and
            await flag.read_flag_value(name_parser, "state") != "completed!"):
        await query.answer(
            text=f'Parser {name_parser.capitalize()} ALREADY exists!',
            show_alert=True
        )
        return

    await bott.send_message(
        chat_id=ADMIN,
        text=f'''{hbold("I'm ready to parse apartments!")}\n\nSelect an action!  📉''',
        reply_markup=main_kb()
    )

    await query.answer(
        text=f'Success Start pars -{name_parser}-',
        show_alert=True
    )

    await flag.update_full_flag(
        key=name_parser,
        new_data={
            "parser_name": name_parser,
            "bool": True,
            "minutes": 0,
            "seconds": 0,
            "state": "in process",
            "errors": await flag.read_flag_value(name_parser, "errors")
        }
    )

    start_time = time.time()

    _parser = start_pars[name_parser][0]
    if start_pars[name_parser][-1] in ['selenium', 'sync']:
        loop = get_event_loop()
        exel: list[str | bool] = await loop.run_in_executor(None, _parser.run, '')
    else:
        exel: list[str | bool] = await _parser.run()

    minutes = int(int(time.time() - start_time) / 60)
    seconds = int(time.time() - start_time) % 60

    await flag.update_full_flag(
        key=name_parser,
        new_data={
            "bool": False,
            "minutes": minutes,
            "seconds": seconds,
            "state": "completed!",
            "errors": await flag.read_flag_value(name_parser, "errors")
        }
    )

    if exel[-1]:
        await bott.send_document(
            chat_id=query.message.chat.id,
            document=FSInputFile(f'{exel[0]}'),

        )
        return
    await query.answer(
        text = f'File -{exel}- was broken (',
        show_alert = True
    )

# /Parsing handlers


# Settings logic
@router.callback_query(lambda query: query.data.startswith('info'))
async def return_calculate_menu(query: CallbackQuery):
    await bott.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )
    flag = FlagsManager()

    await bott.send_message(
        text=await formatted_info_text(fl=flag),
        chat_id=query.message.chat.id,
        reply_markup=info_kb()
    )

@router.callback_query(lambda query: query.data.startswith('clear'))
async def return_calculate_menu(query: CallbackQuery):
    await bott.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )
    flag = FlagsManager()

    await bott.send_message(
        text=await del_unnecessary_info(fl=flag),
        chat_id=query.message.chat.id,
        reply_markup=info_kb()
    )

@router.callback_query(lambda query: query.data.startswith('go_back'))
async def return_calculate_menu(query: CallbackQuery):
    await bott.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )
    await bott.send_message(
        chat_id=ADMIN,
        text=f'''{hbold("I'm ready to parse apartments!")}\n\nSelect an action!  📉''',
        reply_markup=main_kb()
    )
# /Settings logic



# /Parsing List logic
@router.callback_query(lambda query: query.data.startswith('list'))
async def return_calculate_menu(query: CallbackQuery):
    await bott.delete_message(
        chat_id=query.message.chat.id,
        message_id=query.message.message_id
    )

    await bott.send_message(
        chat_id=ADMIN,
        text=PARSING_LIST_TEXT,
        reply_markup=cancel_kb()
    )
# /Parsing List logic