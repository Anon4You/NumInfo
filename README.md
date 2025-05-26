# 🔍 NumInfo - Advanced Phone Number Intelligence Tool

📡 A powerful Python tool for gathering comprehensive information about phone numbers using multiple APIs and data sources.

## 🌟 Features

- ✅ **Phone Number Validation**: Verify if a number is valid and properly formatted
- 📱 **Carrier Lookup**: Identify the service provider for any phone number
- 🌍 **Geolocation**: Determine the country and region associated with a number
- ⏰ **Timezone Detection**: Find the timezone(s) for a phone number
- 🔌 **API Integration**: Supports NumVerify and AbstractAPI (optional)
- 📊 **Multiple Output Formats**: Colorful console output and JSON export
- 🔒 **Privacy Focused**: Only uses publicly available information

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/Anon4You/NumInfo.git
cd NumInfo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Set up environment variables for API features:
```bash
cp .env.example .env
# Edit .env with your API keys
```

## 🚀 Usage

Basic usage:
```bash
python numinfo.py +1234567890
```

Save results to JSON file:
```bash
python numinfo.py +1234567890 -o results.json
```

### ⚙️ Command Line Options
```
positional arguments:
  phone_number          Phone number to investigate (include country code)

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Output file name (JSON format)
```

## 🔑 API Integration

For enhanced features, obtain API keys from:
- [NumVerify](https://numverify.com/) (for carrier details)
- [AbstractAPI](https://www.abstractapi.com/phone-validation-api) (for geolocation)

Add your keys to the `.env` file:
```
NUMVERIFY_API_KEY=your_key_here
ABSTRACT_API_KEY=your_key_here
```
## 🤝 Contributing

We welcome contributions! Please follow these steps:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📬 Contact

👨💻 **Alienkrishn** - [GitHub](https://github.com/Anon4You)  
🔗 Project Link: [https://github.com/Anon4You/NumInfo](https://github.com/Anon4You/NumInfo)
