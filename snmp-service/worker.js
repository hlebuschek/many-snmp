const { parentPort } = require("worker_threads");
const snmp = require("net-snmp");

parentPort.on("message", (data) => {
  const { ip, community } = data;

  const session = snmp.createSession(ip, community);
  const oid = "1.3.6.1"; // Начальная точка для обхода всех OID
  const result = [];

  session.walk(
    oid,
    null, // Убираем ограничение на количество объектов за раз
    (varbind) => {
      varbind.forEach((vb) => {
        try {
          let value = vb.value;

          // Обработка OctetString для представления MAC-адресов и других данных
          if (vb.type === snmp.ObjectType.OctetString) {
            if (Buffer.isBuffer(value) && value.length > 0) {
              // Конвертируем буфер в строку для MAC-адресов
              value = value.toString("hex").match(/.{1,2}/g).join(":");
            } else if (Buffer.isBuffer(value)) {
              value = "(empty buffer)";
            } else {
              value = value ? value.toString() : "(null)";
            }
          }

          // Общая проверка для null и пустых данных
          if (value === null || value === undefined) {
            value = "(null or undefined)";
          }

          result.push({
            oid: vb.oid,
            type: snmp.ObjectType[vb.type] || vb.type,
            value,
          });
        } catch (err) {
          // Логируем ошибки, но продолжаем обработку
          console.warn(`Error processing OID ${vb.oid}:`, err.message);
        }
      });
    },
    (error) => {
      session.close(); // Закрываем сессию
      if (error) {
        console.warn("SNMP Walk Error:", error);
      }
      parentPort.postMessage({ result }); // Возвращаем все собранные данные
    }
  );
});
