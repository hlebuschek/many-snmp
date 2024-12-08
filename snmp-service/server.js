const express = require("express");
const { Worker } = require("worker_threads");

const app = express();
const port = 3000;

app.use(express.json());

function handleSnmpRequest(ip, community) {
  return new Promise((resolve, reject) => {
    const worker = new Worker("./worker.js");
    worker.postMessage({ ip, community });

    worker.on("message", (data) => {
      if (data.error) {
        reject(data.error);
      } else {
        resolve(data.result);
      }
    });

    worker.on("error", (err) => reject(err));
    worker.on("exit", (code) => {
      if (code !== 0) {
        reject(new Error(`Worker stopped with exit code ${code}`));
      }
    });
  });
}

app.post("/snmp", async (req, res) => {
  const { ip, community = "public" } = req.body;

  if (!ip) {
    return res.status(400).send({ error: "IP address is required" });
  }

  try {
    const result = await handleSnmpRequest(ip, community);
    res.send(result);
  } catch (error) {
    res.status(500).send({ error: error.toString() });
  }
});

app.listen(port, () => {
  console.log(`SNMP server is running on http://localhost:${port}`);
});
