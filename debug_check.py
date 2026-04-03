address = "mn_addr_preprod1qr0n4n8lhczmnnjv0ryzvcul3dteals0ejjgs7mmpqueh4u9clqssyv3kd"
network = "preprod"

is_preprod_wallet = (
    network == "preprod" and 
    address == "mn_addr_preprod1qr0n4n8lhczmnnjv0ryzvcul3dteals0ejjgs7mmpqueh4u9clqssyv3kd"
)

print(f"Network: {network}")
print(f"Network == 'preprod': {network == 'preprod'}")
print(f"Address: {address}")
print(f"Address match: {address == 'mn_addr_preprod1qr0n4n8lhczmnnjv0ryzvcul3dteals0ejjgs7mmpqueh4u9clqssyv3kd'}")
print(f"Is preprod wallet: {is_preprod_wallet}")
