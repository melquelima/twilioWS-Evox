import os
from app import app,manager


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)#, use_reloader=False)
    #manager.run()
    #app.run()
    
    