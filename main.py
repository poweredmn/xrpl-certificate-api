from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from xrpl_utils import calculate_hash, submit_payment_transaction, check_hash_in_state

app = FastAPI()


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Read and hash the file
        file_content = await file.read()
        hash_hex = calculate_hash(file_content)

        # Submit payment transaction
        transaction_response = await submit_payment_transaction(hash_hex)

        return JSONResponse(content={
            "status": "success",
            "hash": hash_hex,
            **transaction_response
        })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to process transaction.")


@app.post("/write-hash")
async def write_hash(hash_hex: str):
    try:
        # Submit payment transaction
        transaction_response = await submit_payment_transaction(hash_hex)

        return JSONResponse(content={
            "status": "success",
            "hash": hash_hex,
            **transaction_response
        })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to process transaction.")


@app.post("/get-hash")
async def get_hash(file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        hash_hex = calculate_hash(file_content)

        return JSONResponse(content={
            "status": "success",
            "hash": hash_hex.encode('utf-8').hex()
        })
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to get hash.")


@app.post("/check-hash")
async def check_hash(file: UploadFile = File(...)):
    try:
        # Read and hash the file
        file_content = await file.read()
        hash_hex = calculate_hash(file_content)

        # Check if hash exists in account's state
        state_response = await check_hash_in_state(hash_hex)
        return JSONResponse(content=state_response)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to check hash.")
