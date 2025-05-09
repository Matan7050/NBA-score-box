import sys
import requests
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QHBoxLayout, QScrollArea, QPushButton
)
from PyQt6.QtGui import QMovie, QFont, QFontDatabase, QPixmap
from PyQt6.QtCore import Qt
from nba_api.live.nba.endpoints import scoreboard

# Helper to get team logo
def get_logo_pixmap(team_abbr):
    url = f"https://a.espncdn.com/i/teamlogos/nba/500/{team_abbr.lower()}.png"
    try:
        response = requests.get(url)
        pixmap = QPixmap()
        pixmap.loadFromData(response.content)
        return pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
    except Exception:
        return QPixmap()

class NBALogosApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Live NBA Scores with Logos")
        self.resize(1000, 800)

        # Background animation
        self.bg_label = QLabel(self)
        self.movie = QMovie("lightning.gif")
        self.bg_label.setMovie(self.movie)
        self.movie.start()
        self.bg_label.lower()
        self.bg_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.bg_label.resize(self.width(), self.height())
        self.bg_label.setScaledContents(True)

        # Custom font
        font_id = QFontDatabase.addApplicationFont("fonts/Orbitron-Black.ttf")
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        self.team_font = QFont(font_family, 18)
        self.team_font.setBold(True)

        # Transparent styling
        self.setStyleSheet("background: transparent;")

        self.layout = QVBoxLayout(self)

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.update_scores)
        self.refresh_button.setStyleSheet("background-color: rgba(0, 0, 0, 80); color: white;")
        self.layout.addWidget(self.refresh_button)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("background: transparent; border: none;")

        self.scroll_content = QWidget()
        self.scroll_content.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.update_scores()
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.bg_label.resize(self.size())
    def update_scores(self):
        # Clear old content
        for i in reversed(range(self.scroll_layout.count())):
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        try:
            sb = scoreboard.ScoreBoard()
            data = sb.get_dict()
            games = data["scoreboard"]["games"]

            for game in games:
                home = game["homeTeam"]
                away = game["awayTeam"]
                status = game["gameStatusText"]

                home_abbr = home["teamTricode"]
                away_abbr = away["teamTricode"]

                home_logo = get_logo_pixmap(home_abbr)
                away_logo = get_logo_pixmap(away_abbr)

                row = QHBoxLayout()

                away_logo_label = QLabel()
                away_logo_label.setPixmap(away_logo)
                row.addWidget(away_logo_label)

                away_text = QLabel(f"{away['teamName']} {away['score']}")
                away_text.setFont(self.team_font)
                away_text.setStyleSheet("color: white;")
                row.addWidget(away_text)

                vs_label = QLabel("  vs  ")
                vs_label.setFont(self.team_font)
                vs_label.setStyleSheet("color: white;")
                row.addWidget(vs_label)

                home_text = QLabel(f"{home['teamName']} {home['score']}")
                home_text.setFont(self.team_font)
                home_text.setStyleSheet("color: white;")
                row.addWidget(home_text)

                home_logo_label = QLabel()
                home_logo_label.setPixmap(home_logo)
                row.addWidget(home_logo_label)

                status_label = QLabel(f" ({status})")
                status_label.setFont(self.team_font)
                status_label.setStyleSheet("color: white;")
                row.addWidget(status_label)

                container = QWidget()
                container.setStyleSheet("background: transparent;")
                container.setLayout(row)
                self.scroll_layout.addWidget(container)

        except Exception as e:
            error_label = QLabel(f"Error: {e}")
            error_label.setStyleSheet("color: red;")
            self.scroll_layout.addWidget(error_label)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NBALogosApp()
    window.show()
    sys.exit(app.exec())
