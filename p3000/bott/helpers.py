import aiofiles
import json
from typing import Literal


all_parsers_names = {
    'ivan': [''],
    'vladimir': ['aviator', 'legenda', 'nmarket', 'vladimir_sk'],
    'single': [
        'aviator', 'legenda', 'nmarket', 'vladimir_sk',
    ]
}

class FlagsManager:
    def __init__(self, filepath: str = '__flags.json'):
        self.filepath = filepath

    async def read_flag(self, key: Literal['ivan', 'vladimir', 'all_pars']) -> bool:
        async with aiofiles.open(self.filepath, mode='r') as f:
            content = await f.read()
            data = json.loads(content)
            return data.get(key)

    async def update_flag(self, key: Literal['ivan', 'vladimir', 'all_pars'], value: bool) -> bool:
        try:
            async with aiofiles.open(self.filepath, mode='r') as f:
                content = await f.read()
                data = json.loads(content)

            data[key] = value

            async with aiofiles.open(self.filepath, mode='w') as f:
                await f.write(json.dumps(data, indent=4))

            return True
        except:
            return False