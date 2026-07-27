import yfinance as yf

def fetch_macro_indicators() -> dict:
    try:
        data = yf.download(["^TNX", "GC=F"], period="5d", interval="1d", progress=False)['Close']
        if len(data) < 2:
            return {"gold_change": 0.0, "tnx_change": 0.0}
            
        gold_change = (data["GC=F"].iloc[-1] - data["GC=F"].iloc[-2]) / data["GC=F"].iloc[-2] * 100
        tnx_change = (data["^TNX"].iloc[-1] - data["^TNX"].iloc[-2]) / data["^TNX"].iloc[-2] * 100
        
        return {
            "gold_change": float(gold_change),
            "tnx_change": float(tnx_change)
        }
    except Exception as e:
        print(f"Macro Data Fetch Error: {e}")
        return {"gold_change": 0.0, "tnx_change": 0.0}
