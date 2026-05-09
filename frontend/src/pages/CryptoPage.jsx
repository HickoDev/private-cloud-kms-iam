import { useEffect, useState } from "react";

import { decryptData, encryptData, listKeys } from "../services/keyService.js";

export default function CryptoPage() {
  const [keys, setKeys] = useState([]);
  const [encryptForm, setEncryptForm] = useState({
    keyId: "",
    plaintext: "",
  });
  const [decryptForm, setDecryptForm] = useState({
    keyId: "",
    keyVersion: "",
    ciphertext: "",
    nonce: "",
  });
  const [encryptResult, setEncryptResult] = useState(null);
  const [decryptResult, setDecryptResult] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    async function loadKeys() {
      try {
        const keyData = await listKeys();
        const activeKeys = keyData.filter((key) => key.status === "ACTIVE");
        setKeys(activeKeys);

        if (activeKeys.length > 0) {
          setEncryptForm((current) => ({
            ...current,
            keyId: current.keyId || String(activeKeys[0].id),
          }));
          setDecryptForm((current) => ({
            ...current,
            keyId: current.keyId || String(activeKeys[0].id),
          }));
        }
      } catch (err) {
        setError(err.message);
      }
    }

    loadKeys();
  }, []);

  function updateEncryptForm(field, value) {
    setEncryptForm((current) => ({ ...current, [field]: value }));
  }

  function updateDecryptForm(field, value) {
    setDecryptForm((current) => ({ ...current, [field]: value }));
  }

  async function handleEncrypt(event) {
    event.preventDefault();
    setError("");
    setEncryptResult(null);

    try {
      const result = await encryptData(encryptForm.keyId, encryptForm.plaintext);
      setEncryptResult(result);
      setDecryptForm({
        keyId: String(result.key_id),
        keyVersion: String(result.key_version),
        ciphertext: result.ciphertext,
        nonce: result.nonce,
      });
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDecrypt(event) {
    event.preventDefault();
    setError("");
    setDecryptResult("");

    try {
      const result = await decryptData(decryptForm.keyId, {
        key_version: Number(decryptForm.keyVersion),
        ciphertext: decryptForm.ciphertext,
        nonce: decryptForm.nonce,
      });
      setDecryptResult(result.plaintext);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="page">
      <header className="page-header">
        <div>
          <p className="eyebrow">KMS Operation</p>
          <h1>Encrypt / Decrypt</h1>
        </div>
      </header>

      {error ? <p className="error-message">{error}</p> : null}

      <div className="split-grid">
        <form className="form-panel" onSubmit={handleEncrypt}>
          <h2>Encrypt</h2>
          <label>
            Key
            <select
              value={encryptForm.keyId}
              onChange={(event) => updateEncryptForm("keyId", event.target.value)}
              required
            >
              {keys.length === 0 ? <option value="">No active keys</option> : null}
              {keys.map((key) => (
                <option key={key.id} value={key.id}>
                  {key.name} v{key.active_version}
                </option>
              ))}
            </select>
          </label>
          <label>
            Plaintext
            <textarea
              rows="8"
              value={encryptForm.plaintext}
              onChange={(event) => updateEncryptForm("plaintext", event.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={!encryptForm.keyId}>
            Encrypt
          </button>
          {encryptResult ? (
            <div className="result-box">
              <strong>Version {encryptResult.key_version}</strong>
              <span>{encryptResult.ciphertext}</span>
            </div>
          ) : null}
        </form>

        <form className="form-panel" onSubmit={handleDecrypt}>
          <h2>Decrypt</h2>
          <label>
            Key
            <select
              value={decryptForm.keyId}
              onChange={(event) => updateDecryptForm("keyId", event.target.value)}
              required
            >
              {keys.length === 0 ? <option value="">No active keys</option> : null}
              {keys.map((key) => (
                <option key={key.id} value={key.id}>
                  {key.name}
                </option>
              ))}
            </select>
          </label>
          <label>
            Key version
            <input
              type="number"
              min="1"
              value={decryptForm.keyVersion}
              onChange={(event) => updateDecryptForm("keyVersion", event.target.value)}
              required
            />
          </label>
          <label>
            Ciphertext
            <textarea
              rows="8"
              value={decryptForm.ciphertext}
              onChange={(event) => updateDecryptForm("ciphertext", event.target.value)}
              required
            />
          </label>
          <label>
            Nonce
            <input
              type="text"
              value={decryptForm.nonce}
              onChange={(event) => updateDecryptForm("nonce", event.target.value)}
              required
            />
          </label>
          <button type="submit" disabled={!decryptForm.keyId}>
            Decrypt
          </button>
          {decryptResult ? (
            <div className="result-box">
              <strong>Plaintext</strong>
              <span>{decryptResult}</span>
            </div>
          ) : null}
        </form>
      </div>
    </section>
  );
}
