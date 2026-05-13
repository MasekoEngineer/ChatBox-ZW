from app.main import app

if __name__ == "__main__":
    print("╔════════════════════════════════════════╗")
    print("║       ChatBox ZW - Starting...        ║")
    print("╚════════════════════════════════════════╝")
    print("📍 Server: http://localhost:9007")
    print("💚 Health: http://localhost:9007/health")
    print("📱 USSD:   http://localhost:9007/ussd")
    print("")
    app.run(host="0.0.0.0", port=9007, debug=True)