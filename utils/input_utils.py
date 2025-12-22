from loguru import logger

def input_with_log(prompt):
    """Выводит сообщение input() через логгер и возвращает ввод пользователя"""
    logger.opt(colors=True).info(prompt)
    return input()