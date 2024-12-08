const { parentPort } = require("worker_threads");
const snmp = require("net-snmp");

parentPort.on("message", (data) => {
  const { ip, community } = data;

  const session = snmp.createSession(ip, community);
  const oid = "1.3.6.1"; // Общая начальная точка SNMP
  const result = [];

  session.walk(
    oid,
    20, // Максимальное количество объектов за вызов
    (varbind) => {
      varbind.forEach((vb) => {
        try {
          // Добавляем только доступные OIDs
          result.push({
            oid: vb.oid,
            type: snmp.ObjectType[vb.type],
            value: vb.value.toString(),
          });
        } catch (err) {
          // Логируем, но продолжаем обработку
          console.warn(`Error processing OID ${vb.oid}:`, err.message);
        }
      });
    },
    (error) => {
      session.close(); // Закрываем сессию
      if (error) {
        // Логируем ошибку, но возвращаем уже собранные данные
        console.warn("SNMP Walk Error:", error);
      }
      parentPort.postMessage({ result }); // Возвращаем доступные данные
    }
  );
});
