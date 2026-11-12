"""Trial check: sqlcipher3 keeps a marker string off the disk, refuses a wrong key, and the OS key store works."""
import glob, os, platform, sqlite3, sys
import sqlcipher3

CANARY = b"CANARY-Brightline-9f3a"
print(platform.platform(), "| sqlcipher3", getattr(sqlcipher3, "version", "?"))

def scan(prefix):
    return sorted(os.path.basename(f) for f in glob.glob(prefix + "*") if CANARY in open(f, "rb").read())

con = sqlite3.connect("plain.db"); con.execute("CREATE TABLE t(body TEXT)")
con.execute("INSERT INTO t VALUES (?)", (CANARY.decode(),)); con.commit(); con.close()
control = scan("plain.db")
print("control (plain sqlite) marker found in:", control)

con = sqlcipher3.connect("enc.db"); cur = con.cursor()
cur.execute("PRAGMA key='correct horse'"); cur.execute("PRAGMA journal_mode=WAL")
cur.execute("CREATE TABLE t(id INTEGER PRIMARY KEY, body TEXT)")
cur.execute("INSERT INTO t(body) VALUES (?)", (CANARY.decode() * 50,)); con.commit()
print("cipher_version:", list(cur.execute("PRAGMA cipher_version")), "temp_store:", list(cur.execute("PRAGMA temp_store")))
print("files while open:", sorted(glob.glob("enc.db*")))
leak_open = scan("enc.db"); con.close(); leak_closed = scan("enc.db")
print("marker on disk while open:", leak_open, "| after close:", leak_closed)

def refused(key_sql):
    try:
        c = sqlcipher3.connect("enc.db"); k = c.cursor()
        if key_sql: k.execute(key_sql)
        list(k.execute("SELECT count(*) FROM t")); return False
    except Exception as e:
        print("  refused:", type(e).__name__); return True
wrong, nokey = refused("PRAGMA key='wrong key'"), refused(None)

keyring_ok = None
try:
    import keyring
    print("keyring backend:", keyring.get_keyring())
    keyring.set_password("clause-tracer-trial", "master", "not-a-real-key")
    keyring_ok = keyring.get_password("clause-tracer-trial", "master") == "not-a-real-key"
    keyring.delete_password("clause-tracer-trial", "master")
except Exception as e:
    print("keyring error:", type(e).__name__, e); keyring_ok = False
print("keyring round trip:", keyring_ok)

ok = bool(control) and not leak_open and not leak_closed and wrong and nokey and keyring_ok
print("RESULT store:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
