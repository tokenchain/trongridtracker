def read_file_lines(filename: str) -> list:
    content_line = []
    with open(filename, 'r') as fp:
        for count, content in enumerate(fp):
            tmp = content.strip().replace("\n", "")
            content_line.append(tmp)
        fp.close()
    return content_line


def read_file_at_line(filename: str, line: int) -> str:
    content_line = ""
    with open(filename, 'r') as fp:
        for count, content in enumerate(fp):
            if count == line:
                content_line = content.strip().replace("\n", "")
        fp.close()
    return content_line


def read_file_total_lines(filename: str) -> int:
    print(f"count lines from metamask {filename}")
    with open(filename, 'r') as fp:
        for count, line in enumerate(fp):
            pass
        fp.close()
    print('Total Lines', count + 1)
    return count + 1
