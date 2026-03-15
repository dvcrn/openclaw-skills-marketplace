const { MqttTokenClient } = require("../adapters/mqtt-token-client");
const { MqttTransport } = require("../adapters/mqtt-transport");
const { handleA2aMessage } = require("./router");

async function startA2aService({ cfg, store, logger }) {
  if (!cfg.mqttEndpoint) {
    logger.info("a2a mqtt disabled: missing A2HMARKET_MQTT_ENDPOINT");
    return {
      enabled: false,
      async publishEnvelope() {
        throw new Error("a2a mqtt is disabled");
      },
      async stop() {},
    };
  }
  if (!cfg.agentId || !cfg.agentSecret) {
    logger.warn("a2a mqtt disabled: missing agent credentials");
    return {
      enabled: false,
      async publishEnvelope() {
        throw new Error("a2a mqtt is disabled");
      },
      async stop() {},
    };
  }

  try {
    const tokenClient = new MqttTokenClient(cfg);
    const transport = new MqttTransport({ cfg, tokenClient, logger });
    const publishEnvelope = async (targetAgentId, envelope, qos) => {
      const target = String(targetAgentId || "").trim();
      if (!target) throw new Error("targetAgentId is required");
      if (!envelope || typeof envelope !== "object") {
        throw new Error("envelope must be an object");
      }
      await transport.publishToAgent(target, envelope, qos == null ? 1 : qos);
    };
    const onMessage = (msg) => {
      try {
        logger.info(`a2a processing message topic=${msg.topic} size=${msg.payload.length}b`);
        let envelope = null;
        try {
          envelope = JSON.parse(msg.payload);
          logger.info(
            `a2a envelope parsed sender_id=${envelope.sender_id || '-'} target_id=${envelope.target_id || '-'} message_type=${envelope.message_type || '-'} message_id=${envelope.message_id || '-'}`
          );
          logger.debug(`a2a envelope payload: ${JSON.stringify(envelope.payload || {}).slice(0, 500)}`);
        } catch (err) {
          logger.warn(`a2a message parse failed: ${err.message}`);
          return;
        }
        
        const result = handleA2aMessage({
          topic: msg.topic,
          payload: msg.payload,
          envelope: envelope,
          store,
          cfg,
          logger,
        });
        if (!result.accepted) {
          logger.warn(`a2a message rejected reason=${result.reason} sender_id=${envelope?.sender_id || '-'}`);
          return;
        }
        logger.info(
          `a2a event accepted event_id=${result.event_id} peer_id=${result.peer_id} message_id=${result.message_id || "-"}`
        );
      } catch (err) {
        logger.error(`a2a message handler crashed: ${err.message}`, { stack: err.stack });
      }
    };
    const onConnect = () => {
      transport
        .subscribeIncoming(cfg.agentId)
        .catch((err) => {
          logger.warn(`a2a mqtt resubscribe failed: ${(err && err.message) || String(err)}`);
        });
    };

    await transport.connect({
      agentId: cfg.agentId,
      agentSecret: cfg.agentSecret,
    });
    await transport.subscribeIncoming(cfg.agentId);
    transport.on("connect", onConnect);
    transport.on("message", onMessage);
    logger.info("a2a mqtt service started");
    return {
      enabled: true,
      publishEnvelope,
      async stop() {
        transport.off("connect", onConnect);
        transport.off("message", onMessage);
        transport.close();
      },
    };
  } catch (err) {
    logger.warn(`a2a mqtt disabled: ${(err && err.message) || String(err)}`);
    return {
      enabled: false,
      async publishEnvelope() {
        throw new Error("a2a mqtt is disabled");
      },
      async stop() {},
    };
  }
}

module.exports = {
  startA2aService,
};
