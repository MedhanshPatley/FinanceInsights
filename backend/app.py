from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

@app.route('/api/stock-analysis', methods=['POST'])
def stock_analysis():
    try:
        
        data = request.get_json()
        ticker = data.get('ticker', None)

        if not ticker:
            return jsonify({'error': 'Ticker symbol is required'}), 400

        insights = fetch_insights(ticker)
        return jsonify(insights)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def fetch_insights(ticker):
    try:
        # Fetch stock data from yfinance
        stock = yf.Ticker(ticker)
        data = stock.history(period="1d", interval="1m")

        # Check if data is empty
        if data.empty:
            return {'error': f"No data available for ticker {ticker}"}

        # Extract relevant metrics
        current_price = data['Close'].iloc[-1] if not data['Close'].empty else None
        initial_price = data['Close'].iloc[0] if not data['Close'].empty else None
        info = stock.info or {}

        if current_price is None or initial_price is None:
            return {'error': f"Unable to fetch price data for ticker {ticker}"}

        insights = {
            'Current Price': f"${current_price:.2f}",
            'Growth %': f"{((current_price - initial_price) / initial_price * 100):.2f}%" if initial_price else "N/A",
            'P/E Ratio': info.get('trailingPE', 'N/A'),
            'Market Cap': f"${info.get('marketCap', 'N/A'):,}" if info.get('marketCap') else 'N/A',
            'Dividend Yield': f"{info.get('dividendYield', 0) * 100:.2f}%",
            '52 Week High': f"${info.get('fiftyTwoWeekHigh', 'N/A')}",
            '52 Week Low': f"${info.get('fiftyTwoWeekLow', 'N/A')}"
        }

        # Generate AI analysis (ensure the AI setup is correct)
        # genai.configure(api_key='AIzaSyA-uFsZTUYNEpx58HMrpMDXKP4ogVVmyPc')
        genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
        model = genai.GenerativeModel('gemini-1.5-flash-8b')

        insights_text = "\n".join([f"{k}: {v}" for k, v in insights.items()])
        prompt = f"Provide a concise stock analysis for {ticker} based on these metrics:\n{'  '.join([f'{k}: {v}' for k, v in insights.items()])}"

        response = model.generate_content(prompt)
        analysis = f"""
        Stock Analysis for {ticker}
Key Metrics:

Current Price: {insights['Current Price']}
52 Week High: {insights['52 Week High']}
52 Week Low: {insights['52 Week Low']}
Dividend Yield: {insights['Dividend Yield']}
Growth %: {insights['Growth %']}
Market Cap: {insights['Market Cap']}
P/E Ratio: {insights['P/E Ratio']}

Analysis:
The current stock price of {ticker} is {insights['Current Price']}, which is down slightly from its 52-week high of {insights['52 Week High']} and 52-week low of {insights['52 Week Low']}. This wide price range indicates volatility in the stock.
The company's P/E ratio of {insights['P/E Ratio']} and dividend yield of {insights['Dividend Yield']} suggest moderate valuation and income potential. Its large market cap of {insights['Market Cap']} implies it is a significant player in the industry.
However, the negative growth percentage of {insights['Growth %']} is a concerning trend that warrants further investigation. Additional analysis of the company's financials, industry positioning, and strategic initiatives would be needed to fully assess the outlook.
In summary, {ticker} displays both strengths and risks based on the current metrics. A deeper dive into the underlying factors driving performance is recommended to determine if this is a temporary blip or a more significant trend.
"""
        return {
            'metrics': insights,
            'aiAnalysis': analysis
        }

    except Exception as e:
        return {'error': str(e)}


if __name__ == '__main__':
    app.run(debug=True)
