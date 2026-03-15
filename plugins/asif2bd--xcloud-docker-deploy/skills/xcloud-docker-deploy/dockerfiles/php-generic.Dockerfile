# Generic PHP + Apache Dockerfile
# Works for CodeIgniter, Symfony, Slim, or any PHP app

FROM php:8.3-apache

RUN a2enmod rewrite headers

RUN docker-php-ext-install pdo pdo_mysql mysqli bcmath

COPY --from=composer:2.7 /usr/bin/composer /usr/bin/composer

ENV APACHE_DOCUMENT_ROOT=/var/www/html/public
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf && \
    sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf

WORKDIR /var/www/html

COPY composer.json composer.lock* ./
RUN composer install --no-dev --no-scripts --no-autoloader --prefer-dist

COPY . .
RUN composer dump-autoload --optimize

RUN chown -R www-data:www-data /var/www/html

EXPOSE 80
CMD ["apache2-foreground"]
