"""
Finovate Audit Nexus AI - Financial Chart Component
Plotly-based financial charts for analytics dashboard.
"""

import plotly.graph_objects as go
from plotly.offline import plot
from typing import List, Dict, Any, Optional
from pathlib import Path


class FinancialChart:
    """Generate professional financial charts using Plotly."""
    
    def __init__(self, theme: str = "dark"):
        self.theme = theme
        self.template = "plotly_dark" if theme == "dark" else "plotly_white"
        
        # Professional color palette
        self.colors = {
            "primary": "#0f3460",
            "secondary": "#e94560",
            "success": "#00c853",
            "warning": "#ffd600",
            "error": "#ff3d00",
            "info": "#2979ff",
            "neutral": "#757575"
        }
    
    def create_trend_chart(self, data: List[Dict], title: str = "Financial Trend", 
                           x_key: str = "period", y_keys: List[str] = None,
                           output_path: str = None) -> str:
        """Create a multi-line trend chart for financial data."""
        fig = go.Figure()
        
        if not y_keys:
            y_keys = [key for key in data[0].keys() if key != x_key]
        
        for y_key in y_keys:
            fig.add_trace(go.Scatter(
                x=[item[x_key] for item in data],
                y=[item[y_key] for item in data],
                mode='lines+markers',
                name=y_key.replace('_', ' ').title(),
                line=dict(width=3),
                marker=dict(size=8)
            ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, family="Segoe UI")),
            xaxis_title=x_key.replace('_', ' ').title(),
            yaxis_title="Value",
            template=self.template,
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_bar_chart(self, categories: List[str], values: List[float], 
                         title: str = "Financial Analysis", 
                         color: str = None, output_path: str = None) -> str:
        """Create a bar chart for categorical financial data."""
        if not color:
            color = self.colors["primary"]
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=categories,
            y=values,
            marker_color=color,
            text=[f"{v:,.2f}" for v in values],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Value: %{y:,.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, family="Segoe UI")),
            xaxis_title="Category",
            yaxis_title="Value",
            template=self.template,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_pie_chart(self, labels: List[str], values: List[float], 
                         title: str = "Distribution", output_path: str = None) -> str:
        """Create a pie/donut chart for financial distribution."""
        colors = [
            self.colors["primary"],
            self.colors["secondary"],
            self.colors["success"],
            self.colors["warning"],
            self.colors["info"],
            self.colors["neutral"]
        ][:len(labels)]
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            hole=0.4,  # Donut chart
            marker_colors=colors,
            textinfo='percent+label',
            hovertemplate='<b>%{label}</b><br>Value: %{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, family="Segoe UI")),
            template=self.template,
            showlegend=True,
            legend=dict(orientation="v", x=1, y=0.5),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_heatmap(self, data: List[List[float]], x_labels: List[str], 
                       y_labels: List[str], title: str = "Risk Heatmap",
                       output_path: str = None) -> str:
        """Create a heatmap for risk analysis or correlation matrix."""
        fig = go.Figure(data=go.Heatmap(
            z=data,
            x=x_labels,
            y=y_labels,
            colorscale='RdYlGn_r',  # Red-Yellow-Green (reversed for risk)
            hovertemplate='%{x} vs %{y}<br>Risk: %{z:.2f}<extra></extra>',
            colorbar=dict(title="Risk Level")
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, family="Segoe UI")),
            xaxis_title="Category",
            yaxis_title="Category",
            template=self.template,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_waterfall_chart(self, labels: List[str], values: List[float], 
                                title: str = "Waterfall Analysis",
                                output_path: str = None) -> str:
        """Create a waterfall chart for financial statement analysis."""
        # Calculate measures: 0=absolute, 1=relative (increasing), -1=relative (decreasing)
        measures = []
        running_total = 0
        
        for i, value in enumerate(values):
            if i == 0 or i == len(values) - 1:
                measures.append("absolute")
            elif value >= 0:
                measures.append("relative")
            else:
                measures.append("relative")
            
            running_total += value
        
        # Create waterfall
        fig = go.Figure(go.Waterfall(
            name="Financial Waterfall",
            orientation="v",
            measure=measures,
            x=labels,
            textposition="outside",
            text=[f"{v:,.2f}" for v in values],
            y=values,
            connector=dict(line=dict(color=self.colors["neutral"])),
            increasing={"marker": {"color": self.colors["success"]}},
            decreasing={"marker": {"color": self.colors["error"]}},
            totals={"marker": {"color": self.colors["primary"]}}
        ))
        
        fig.update_layout(
            title=dict(text=title, font=dict(size=20, family="Segoe UI")),
            showlegend=False,
            template=self.template,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        if output_path:
            plot(fig, filename=output_path, auto_open=False)
            return output_path
        
        return fig.to_html(include_plotlyjs='cdn')
    
    def create_kpi_cards_data(self, kpis: Dict[str, Any]) -> List[Dict]:
        """Prepare KPI data for dashboard cards."""
        cards = []
        
        for name, value in kpis.items():
            status = "normal"
            if isinstance(value, (int, float)):
                if value > 0:
                    status = "success"
                elif value < 0:
                    status = "error"
            
            cards.append({
                "title": name.replace('_', ' ').title(),
                "value": f"{value:,.2f}" if isinstance(value, (int, float)) else str(value),
                "status": status
            })
        
        return cards
