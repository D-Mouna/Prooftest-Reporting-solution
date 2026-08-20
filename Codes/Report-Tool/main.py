import OpenOPC
import pythoncom

def main():
    # Initialize COM for this thread
    pythoncom.CoInitialize()
    try:
        # Create an OPC client instance
        opc = OpenOPC.client()
       
        # Ask Windows for a list of all registered OPC servers
        # This will help us find the exact ProgID of your HIMA server
        print("Discovering OPC servers on this machine...")
        servers = opc.servers()
        print(f"Found {len(servers)} OPC server(s):")
        for server in servers:
            print(f"  - {server}")
       
        # ATTENTION: Look for a server name that contains "HIMA" in the list above.
        # Copy that exact name. We'll use it in the next step.
       
        opc.close()
    except Exception as e:
        print(f"Test failed. Error: {e}")
    finally:
        pythoncom.CoUninitialize()

if __name__ == "__main__":
    main()
