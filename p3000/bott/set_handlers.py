from aiogram.types import CallbackQuery

from .core import router


@router.callback_query(lambda query: query.data.startswith('vladimir'))
async def return_calculate_menu(query: CallbackQuery):
    await query.answer(
        text='Success Start pars VLADIMIR',
        show_alert=True
    )

@router.callback_query(lambda query: query.data.startswith('ivan'))
async def return_calculate_menu(query: CallbackQuery):
    await query.answer(
        text='Success Start pars IVANOVO',
        show_alert=True
    )


@router.callback_query(lambda query: query.data.startswith('pars_all'))
async def return_calculate_menu(query: CallbackQuery):
    await query.answer(
        text='Success Start pars ALL_OBJECTS',
        show_alert=True
    )

@router.callback_query(lambda query: query.data.startswith('info'))
async def return_calculate_menu(query: CallbackQuery):
    ...