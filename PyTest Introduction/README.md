## 🔐 Environment Variables

Set your ReportPortal API key:

Mac/Linux:
export RP_API_KEY=your_api_key  

Windows (PowerShell):
$env:RP_API_KEY="your_api_key"  

---

## 🧩 Configuration (pytest.ini)

[pytest]  
rp_endpoint = https://reportportal.epam.com  
rp_project = YOUR_PROJECT_NAME  
rp_api_key = %(RP_API_KEY)s  
rp_launch = Pytest Homework Launch  
rp_mode = DEFAULT  
rp_enabled = True  

---

## ▶️ Run Tests

pytest --reportportal  

Each run creates a new launch in ReportPortal.

---

## 📊 ReportPortal Dashboard

After running tests:

- Open ReportPortal  
- Select your project  
- Open your launch  
- Create a dashboard  
- Add widgets:
  - Launch execution statistics  
  - Test results trend  
  - Top failed test cases  

---

## 🧪 Example Tests

- CSV validation tests  
- Email format validation  
- Active player checks  

---

