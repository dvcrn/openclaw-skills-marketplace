# Multi-stage Laravel Dockerfile
# xCloud: pair with compose-templates/laravel-mysql.yml

FROM php:8.3-fpm-alpine AS base

RUN apk add --no-cache git curl libpng-dev libxml2-dev zip unzip nodejs npm

RUN docker-php-ext-install pdo pdo_mysql bcmath gd xml zip opcache

RUN pecl install redis && docker-php-ext-enable redis

RUN echo "opcache.enable=1" >> /usr/local/etc/php/conf.d/opcache.ini && \
    echo "opcache.memory_consumption=256" >> /usr/local/etc/php/conf.d/opcache.ini && \
    echo "opcache.max_accelerated_files=20000" >> /usr/local/etc/php/conf.d/opcache.ini && \
    echo "opcache.validate_timestamps=0" >> /usr/local/etc/php/conf.d/opcache.ini

COPY --from=composer:2.7 /usr/bin/composer /usr/bin/composer

WORKDIR /var/www/html

COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --no-autoloader --prefer-dist

COPY . .

RUN composer dump-autoload --optimize

RUN chown -R www-data:www-data /var/www/html/storage /var/www/html/bootstrap/cache

RUN php artisan config:clear && \
    php artisan route:cache && \
    php artisan view:cache

EXPOSE 9000
CMD ["php-fpm"]
