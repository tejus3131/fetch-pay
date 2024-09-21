import json
from time import sleep
from concurrent.futures import ThreadPoolExecutor
import cv2  # type: ignore
import qrcode  # type: ignore
import customtkinter  # type: ignore
from PIL import Image  # type: ignore
import threading
import tkinter
import asyncio


from dotenv import load_dotenv  # type: ignore
import os


from uagents.query import query  # type: ignore
from uagents.envelope import Envelope  # type: ignore

from models import AuthRequest, TransactionRequest, AddressRequest  # type: ignore
from utils import get_address  # type: ignore


load_dotenv()


class PaymentPage(customtkinter.CTkFrame):

    def __init__(self, master, id, reset, **kwargs):
        super().__init__(master, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=1)

        self.id = id

        self.reset = reset

        self.label = customtkinter.CTkLabel(master=self, text="Payment Page")
        self.label.grid(row=0, column=0, padx=20, pady=10, columnspan=2)

        self.reciever = customtkinter.CTkLabel(master=self)
        self.reciever.grid(row=1, column=0, padx=20, pady=10, columnspan=2)

        self.amount_label = customtkinter.CTkLabel(master=self, text="Amount")
        self.amount_label.grid(row=2, column=0, padx=20, pady=10)

        self.amount = tkinter.StringVar()
        self.amount_entry = customtkinter.CTkEntry(
            master=self, placeholder_text="Enter Amount to pay", textvariable=self.amount)
        self.amount_entry.grid(row=2, column=1, padx=20, pady=10)

        self.code_label = customtkinter.CTkLabel(
            master=self, text="Security Code")
        self.code_label.grid(row=3, column=0, padx=20, pady=10)

        self.code = tkinter.StringVar()
        self.code_entry = customtkinter.CTkEntry(
            master=self, placeholder_text="Enter Code", textvariable=self.code)
        self.code_entry.grid(row=3, column=1, padx=20, pady=10)

        self.pay_button = customtkinter.CTkButton(
            master=self, text="Pay", command=self.pay)
        self.pay_button.grid(row=4, column=0, padx=20, pady=10)

        self.cancel_button = customtkinter.CTkButton(
            master=self, text="Cancel", command=self.cancel)
        self.cancel_button.grid(row=4, column=1, padx=20, pady=10)

        self.processing = customtkinter.CTkLabel(master=self, text="")

    def display(self, id, name):
        self.reciever_id = id
        self.reciver_name = name
        self.reciever.configure(text=f"Reciever: {self.reciver_name}({id})")
        self.grid(row=0, column=0, padx=20, pady=20)

    def pay(self):
        self.pay_button.grid_forget()
        self.cancel_button.grid_forget()

        self.processing.configure(text="Processing...")
        self.processing.grid(row=4, column=0, padx=20, pady=10, columnspan=2)

        code = self.code.get()
        amount = self.amount.get()
        threading.Thread(target=self.run_async_process, args=(code, amount)).start()

    def run_async_process(self, code, amount):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        loop.run_until_complete(self.start_process(code, amount))
        
        loop.close()

    async def start_process(self, code, amount):
        result = await self.process(code, amount)

        print("Process result:", result)

        self.processing.configure(text=result)
        await asyncio.sleep(3)

        self.processing.grid_forget()
        self.pay_button.grid(row=4, column=0, padx=20, pady=10)
        self.cancel_button.grid(row=4, column=1, padx=20, pady=10)

        self.cancel()

    async def process(self, code, amount):
        print("Processing...")

        to_address = await query(
            destination=get_address(os.getenv("ADDRESS_EXCHANGE_NAME")),
            message=AddressRequest(id=self.reciever_id),
            timeout=240.0
        )

        if not isinstance(to_address, Envelope):
            return "Unable to process request..."

        to_address = json.loads(to_address.decode_payload())

        if "message" in to_address:
            return to_address["message"]

        from_address = await query(
            destination=get_address(os.getenv("ADDRESS_EXCHANGE_NAME")),
            message=AddressRequest(id=self.id),
            timeout=240.0
        )

        if not isinstance(from_address, Envelope):
            return "Unable to process request..."

        from_address = json.loads(from_address.decode_payload())

        if "message" in from_address:
            return from_address["message"]

        req = TransactionRequest(
            wallet=to_address["wallet"],
            amount=amount,
            code=code
        )

        trac = await query(destination=from_address["address"], message=req, timeout=240.0)

        if not isinstance(trac, Envelope):
            return "Unable to process request..."

        trac = json.loads(trac.decode_payload())

        print(f'returning trac["message"]={trac["message"]}')

        return trac["message"]

    def cancel(self):
        self.amount.set("")
        self.code.set("")
        self.reset()


class QRCodeScanner(customtkinter.CTkFrame):
    def __init__(self, master, id, name, **kwargs):
        super().__init__(master, **kwargs)
        self.executor = ThreadPoolExecutor(max_workers=1)

        self.label = customtkinter.CTkLabel(master=self, text="")
        self.label.grid(row=0, column=0, padx=20, pady=10)

        self.start_button = customtkinter.CTkButton(
            master=self, text="Start Scan", command=self.start_scan)
        self.start_button.grid(row=2, column=0, padx=20, pady=10)

        self.payment_page = PaymentPage(master=self, id=id, reset=self.reset)

        self.username = name

    def reset(self):
        self.label.configure(text="")
        self.start_button.grid(row=2, column=0, padx=20, pady=10)
        self.payment_page.grid_forget()

    def scan_qr_code_with_tkinter(self):
        cap = cv2.VideoCapture(0)
        detector = cv2.QRCodeDetector()

        self.label.configure(text="")

        self.stop_button = customtkinter.CTkButton(
            master=self, text="Stop Scan", command=lambda: self.stop_scan(cap))
        self.stop_button.grid(row=2, column=0, padx=20, pady=10)

        def update_frame():
            ret, frame = cap.read()
            if ret:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(cv2image)

                # Convert the image to a CTkImage
                imgtk = customtkinter.CTkImage(
                    light_image=img, size=(250, 250))

                self.label.configure(image=imgtk)

                decoded_info, _, _ = detector.detectAndDecode(frame)

                if decoded_info:
                    self.stop_scan(cap)
                    self.start_button.grid_forget()
                    self.label.configure(text="Loading...")  # Show the result
                    if self.verify(decoded_info):
                        self.payment_page.display(
                            decoded_info, self.reciver_name)
                    else:
                        self.label.configure(
                            text=f"Error: {self.error}")
                        self.start_button.grid(
                            row=2, column=0, padx=20, pady=10)
                    return

            self.after(10, update_frame)

        update_frame()

    def verify(self, data):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            self.executor, lambda: asyncio.run(self.verify_id(data)))

        self.status = None
        while not self.status:
            sleep(1)
            print("Waiting for status...")

        return self.status

    async def verify_id(self, data):
        status = await query(destination=get_address(os.getenv("ADDRESS_EXCHANGE_NAME")), message=AuthRequest(id=data), timeout=240.0)
        print(status)
        if isinstance(status, Envelope):
            status = json.loads(status.decode_payload())
            print(status)
            if "message" in status:
                self.status = False
                self.error = status['message']
            else:
                self.status = True
                self.reciver_name = status['name']
        else:
            self.status = False
            self.error = "Unable to process request..."

    def start_scan(self):
        # Reset the result label
        self.label.configure(text="Starting Camera...")
        self.start_button.grid_forget()  # Hide the start button
        self.scan_thread = threading.Thread(
            target=self.scan_qr_code_with_tkinter, daemon=True)
        self.scan_thread.start()

    def stop_scan(self, cap):
        cap.release()  # Release the camera when stopping
        self.start_button.grid(row=2, column=0, padx=20,
                               pady=10)  # Show the start button
        self.stop_button.destroy()
        self.label.configure(image='')  # Clear the camera feed
        return


class QRCodeGenerator(customtkinter.CTkFrame):
    def __init__(self, master, id, name, **kwargs):
        super().__init__(master, **kwargs)

        self.name = customtkinter.CTkLabel(
            master=self, text=f"Welcome {name}")
        self.name.grid(row=0, column=0, padx=20, pady=10)
        self.qr_preview = customtkinter.CTkLabel(master=self, text="")
        self.qr_preview.configure(image=self.generate_qr_code(data=str(id)))
        self.qr_preview.grid(row=1, column=0, padx=20, pady=10)

    def generate_qr_code(self, data):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        qr_image = qr.make_image(fill='black', back_color='white')
        return customtkinter.CTkImage(light_image=qr_image.convert("RGB"), size=(250, 250))


class Tabs(customtkinter.CTkTabview):
    def __init__(self, master, id, name, **kwargs):
        super().__init__(master, **kwargs)

        # create tabs
        self.add("My QR Code")
        self.add("Scan QR Code")

        # add widgets on tabs
        self.qr_code_generator = QRCodeGenerator(
            master=self.tab("My QR Code"), id=id, name=name)
        self.qr_code_generator.pack()

        self.qr_code_scanner = QRCodeScanner(
            master=self.tab("Scan QR Code"), id=id, name=name)
        self.qr_code_scanner.pack()


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.title("Fetch-Pay")
        self.executor = ThreadPoolExecutor(max_workers=1)

        self.id = tkinter.StringVar()
        self.id_entry = customtkinter.CTkEntry(
            master=self, placeholder_text="Enter ID", textvariable=self.id)
        self.id_entry.grid(row=1, column=0, padx=20, pady=10)

        self.submit_button = customtkinter.CTkButton(
            master=self, text="Submit", command=self.authenticate_callback)
        self.submit_button.grid(row=2, column=0, padx=20, pady=10)

        self.message = customtkinter.CTkLabel(master=self, text="")
        self.message.grid(row=10, column=0, padx=20, pady=10)

    def authenticate_callback(self):
        loop = asyncio.get_event_loop()
        loop.run_in_executor(
            self.executor, lambda: asyncio.run(self.authenticate()))

    async def authenticate(self):
        self.submit_button.grid_forget()

        if not self.id.get():
            self.message.configure(text="ID is required")
            self.submit_button.grid(row=2, column=0, padx=20, pady=10)
            return

        status = await query(destination=get_address(os.getenv("ADDRESS_EXCHANGE_NAME")), message=AuthRequest(id=self.id.get()), timeout=240.0)

        print(status)

        if not isinstance(status, Envelope):
            self.message.configure(text="Unable to process request...")
            self.submit_button.grid(row=2, column=0, padx=20, pady=10)
            return

        status = json.loads(status.decode_payload())

        print(status)

        if "message" in status:
            self.message.configure(text=status['message'])
            self.submit_button.grid(row=2, column=0, padx=20, pady=10)
        else:
            self.show_tabs(status['name'])

    def show_tabs(self, name):
        self.id_entry.grid_forget()
        self.submit_button.grid_forget()
        self.tab_view = Tabs(master=self, id=self.id.get(), name=name)
        self.tab_view.grid(row=0, column=0, padx=20, pady=20)


def main() -> None:
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
