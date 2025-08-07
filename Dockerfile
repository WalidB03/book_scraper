FROM pwbase:v1
COPY --chown=appuser:appuser ./app/ /home/appuser/app/
WORKDIR /home/appuser/app/
USER appuser
ENTRYPOINT ["python", "main.py"]

#> docker build -t book_scraper:v1 ./
#> docker run -it --rm --init --security-opt seccomp=seccomp_profile.json -v ./app/:/home/appuser/app/ books_scraper:v1
