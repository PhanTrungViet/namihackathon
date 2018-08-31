#!/usr/bin/env python3

from flask import Flask, request, json, render_template

from blockchain import Blockchain, BlockNotFound

app = Flask(__name__)
blockchain = Blockchain()

@app.route("/")
def index():
    block_count = len(blockchain.blocks)
    last_10_blocks = []
    for block in blockchain.blocks[:-11:-1]:
        last_10_blocks.append(block.hash_hex())
    return render_template("index.html", block_count = block_count, last_10_blocks = last_10_blocks,
                                         unconfirmed_txs = blockchain.tx_queue)

@app.route("/block/<id>")
def block(id):
    try:
        block = blockchain.get_block_with_id(id)
        return render_template("block.html", block = block)
    except BlockNotFound:
        return "Block not found"

@app.route("/set", methods = ["POST"])
def blockchain_set():
    key = request.values['key']
    value = request.values['value']

    blockchain.set_key(key, value)

    return json.jsonify({
        "result": "ok",
    })


@app.route("/get", methods = ["GET"])
def blockchain_get():
    key = request.values['key']

    try:
        value = blockchain.get_key(key)
        return json.jsonify({
            "result": "ok",
            "value" : value
        })
    except:
        return json.jsonify({
            "result" : "error",
            "err_msg": "Key not found. Maybe the key definitely does not exist, or the transaction hasn't been included yet"
        })


@app.route("/check", methods = ["GET"])
def blockchain_check():
    key = request.values['key']

    try:
        value = blockchain.get_key(key)
        return json.jsonify({
            "result": "included",
        })
    except:
        if blockchain.tx_in_queue(key):
            return json.jsonify({
                "result": "queued",
            })
        else:
            return json.jsonify({
                "result": "404",
            })


@app.route("/get_mining_template", methods = ["GET"])
def get_mining_template():
    return json.jsonify({
        "result"  : "ok",
        "template": blockchain.get_mining_template().to_bytes().hex(),
        "target": blockchain.get_current_target().hex()
    })


@app.route("/submit_block", methods = ["POST"])
def submit_block():
    block = request.values['block']
    b = bytes.fromhex(block)
    blockchain.add_raw_block(b)

    return json.jsonify({
        "result": "ok"
    })


if __name__ == "__main__":
    app.run(debug = True)
