# Walled project - python meetup BCN

## components

- walledapiapp.py: API
- tasks.py: celery tasks
- interactivewalledbot.py: Telegram Bot
- rpi_framebuffer_walled_client.py: Raspberry client that outputs to framebuffer

## how to run

### In the server:

- Check that redis is running
- start api: python walledapiapp.py
- start celery: celery -A 
- start bot: interactivewalledbot.py

### In the raspberry pi

- sudo python rpi_framebuffer_walled_client.py WALLED_API_URL WALL_ID