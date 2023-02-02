from glob import iglob
import os
import re
from pathlib import Path

import docx2txt


def main():
    result: dict[str, list[str]] = {}

    for file_path in iglob(os.path.join(os.getcwd(), '*.docx')):
        name = file_path
        name = os.path.basename(name)
        print(f'Process {name}...')
        result[name] = extract_text_from_docx_file(file_path)

        with open(Path(file_path).with_suffix('.txt'), 'w') as fp:
            fp.writelines(map(lambda x: f'{x}\n', result[name]))


def extract_text_from_docx_file(file_path: str) -> list[str]:
    text = docx2txt.process(file_path)
    result = text.splitlines()
    result = map(lambda x: x.strip(), result)
    result = map(lambda x: re.sub(r"[\xa0[:space:]]+", " ", x), result)
    result = filter(None, result)

    return list(result)


if __name__ == '__main__':
    main()
