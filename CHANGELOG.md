# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Calendar Versioning](https://calver.org/) of
the following form: YYYY.0M.0D.

## 2024.11.22

### Added

- Tutorial link in ReadMe

## 2024.11.19

### Added

- Changelog
- Gitignore

### Updated

- Made Geoapify API Calls biased towards US locations
- Uses first US geocoding coordinates returned by Geoapify geocoder instead of the first result in the world
- ReadMe to include information about Geoapify

## 2024.11.14

### Added

- Streamlit Caching

### Updated

- Updated autocomplete to not display suggestions that were outside the US

## 2024.11.12

### Added

- Autocomplete suggestions that appear when a user enters a city

## 2024.10.17

### Added

- Description of the project in ReadMe
- Error messages for issues with API calls

### Removed

- The initial program that tested WeatherGov API calls (WeatherGov.py)

## 2024.10.15

### Added

- Proper Geoapify attribution in Streamlit Dashboard

### Updated

- Switched to Geoapify for geocoding

### Removed

- OpenMeteo sample API call code

## 2024.10.8

### Added

- Main Streamlit dashboard that displays a graph for a user inputted location. It uses Nominatim geocoding and WeatherGov API calls

## 2024.10.1

### Added

- Simple sample Streamlit dashboard that displays a graph for a hard coded location (Proof of Concept)
- ReadMe file with links to Streamlit Dashboards

## 2024.9.26

### Added

- A simple Matplotlib graph from a hard coded WeatherGov API call

## 2024.9.19

### Added

- OpenMeteo sample API call code
