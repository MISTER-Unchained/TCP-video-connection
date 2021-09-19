byte_string = b'\\FF\\D8\\FF\\E0\\00\\10\\4A\\46\\49\\46\\00\\01\\01\\01\\01\\2C\\01\\2C\\00\\00\\FF\\E1\\00\\5D\\45\\78\\69\\66\\00\\00\\49\\49\\xff\\xd9'


def check_data_end(data):
    for i in range(0, len(data), 1):
        print(data[i:i+10])
        if data[i:i+10] == b"\\xff\\xd9":
            return True
        else: 
            continue
    return False