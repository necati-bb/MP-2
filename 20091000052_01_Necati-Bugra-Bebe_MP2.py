import tkinter as tk
from tkinter import messagebox
import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class OlympicMedalTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Olympic Medal Tracker - Paris 2024")
        self.root.geometry("800x600")


        tk.Label(root, text="Enter Medal Data URL:").pack(pady=5)

        self.url_entry = tk.Entry(root, width=70)
        self.url_entry.pack(pady=5)
        self.url_entry.insert(0, "https://www.bbc.com/sport/olympics/paris-2024/medals")


        tk.Button(root, text="Load Countries", command=self.scrape_medal_data).pack(pady=5)

        # Countries Listbox
        self.countries_listbox = tk.Listbox(root, width=50, height=10)
        self.countries_listbox.pack(pady=10)


        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        tk.Button(button_frame, text="Country Medal Chart", command=self.show_country_chart).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="General Analytics", command=self.show_general_analytics).pack(side=tk.LEFT, padx=5)


        self.df = None

    def scrape_medal_data(self):
        """Scrape medal data from the provided URL"""
        try:

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            url = self.url_entry.get()
            response = requests.get(url, headers=headers)
            response.raise_for_status()


            soup = BeautifulSoup(response.text, 'html.parser')


            countries = []
            gold_medals = []
            silver_medals = []
            bronze_medals = []


            table_rows = soup.find_all('tr')[1:]  # Skip header
            for row in table_rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    countries.append(cols[1].text.strip())
                    gold_medals.append(int(cols[2].text.strip() or 0))
                    silver_medals.append(int(cols[3].text.strip() or 0))
                    bronze_medals.append(int(cols[4].text.strip() or 0))


            self.df = pd.DataFrame({
                'Country': countries,
                'Gold': gold_medals,
                'Silver': silver_medals,
                'Bronze': bronze_medals
            })


            self.df['Total'] = self.df['Gold'] + self.df['Silver'] + self.df['Bronze']


            self.countries_listbox.delete(0, tk.END)
            for country in self.df['Country']:
                self.countries_listbox.insert(tk.END, country)

            messagebox.showinfo("Success", f"{len(self.df)} countries loaded!")

        except Exception as e:
            messagebox.showerror("Error", f"Could not load data: {str(e)}")

    def show_country_chart(self):
        """Show bar chart for selected country"""
        if self.df is None:
            messagebox.showerror("Error", "Please load data first")
            return


        selected_indices = self.countries_listbox.curselection()
        if not selected_indices:
            messagebox.showerror("Error", "Please select a country")
            return

        country = self.countries_listbox.get(selected_indices[0])
        country_data = self.df[self.df['Country'] == country]


        plt.figure(figsize=(8, 5))
        medal_types = ['Gold', 'Silver', 'Bronze']
        medal_counts = [
            country_data['Gold'].values[0],
            country_data['Silver'].values[0],
            country_data['Bronze'].values[0]
        ]

        plt.bar(medal_types, medal_counts, color=['gold', 'silver', 'brown'])
        plt.title(f'{country} Medal Counts')
        plt.ylabel('Number of Medals')


        chart_window = tk.Toplevel(self.root)
        chart_window.title(f"{country} Medal Chart")


        canvas = FigureCanvasTkAgg(plt.gcf(), master=chart_window)
        canvas.draw()
        canvas.get_tk_widget().pack()

    def show_general_analytics(self):
        """Show general analytics with pie and line charts"""
        if self.df is None:
            messagebox.showerror("Error", "Please load data first")
            return


        top_countries = self.df.nlargest(10, 'Total')

        # Create a new window for analytics
        analytics_window = tk.Toplevel(self.root)
        analytics_window.title("Olympic Medal Analytics")
        analytics_window.geometry("1200x800")


        fig, axs = plt.subplots(2, 2, figsize=(15, 10))


        axs[0, 0].pie(top_countries['Gold'], labels=top_countries['Country'], autopct='%1.1f%%')
        axs[0, 0].set_title('Gold Medals Distribution (Top 10)')


        axs[0, 1].pie(top_countries['Silver'], labels=top_countries['Country'], autopct='%1.1f%%')
        axs[0, 1].set_title('Silver Medals Distribution (Top 10)')


        axs[1, 0].pie(top_countries['Bronze'], labels=top_countries['Country'], autopct='%1.1f%%')
        axs[1, 0].set_title('Bronze Medals Distribution (Top 10)')


        axs[1, 1].plot(top_countries['Country'], top_countries['Total'], marker='o')
        axs[1, 1].set_title('Total Medals by Top 10 Countries')
        axs[1, 1].set_xlabel('Countries')
        axs[1, 1].set_ylabel('Total Medals')
        axs[1, 1].tick_params(axis='x', rotation=45)

        plt.tight_layout()


        canvas = FigureCanvasTkAgg(fig, master=analytics_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)


def main():
    root = tk.Tk()
    app = OlympicMedalTracker(root)
    root.mainloop()


if __name__ == "__main__":
    main()

    # reference: https://github.com/udhavvvv-dev/Olympic-Data-Analysis
    # reference: https: // www.kaggle.com / code / amankhan98 / olympics - 2024 - analysis
    # reference: https://github.com/Kanangnut/Paris-Olympic-2024-Dashboard-Analysis