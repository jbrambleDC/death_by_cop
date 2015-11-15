import pandas as pd
import us
import numpy as np
from bokeh.plotting import figure, show, output_file

data = pd.read_csv('data/KBP-2013-14-15-FULL-DFE.csv')
state_pops = pd.read_csv('data/state_pops.csv')
state_pops = state_pops[["NAME", "POPESTIMATE2012"]]

def count_by_state(df):
  return df.groupby(["State"]).size()

def normalized_count(ser, df):
  df = df.set_index('NAME')
  df = pd.concat([ser, df], axis=1).reset_index()
  df.columns = ['State', 'deaths', 'population']

  df = df[np.isfinite(df["deaths"])]
  df = df[np.isfinite(df["population"])]

  df["Death_per_capita"] = df["deaths"]/df["population"]*1000
  return df[["State", "Death_per_capita"]]

def get_by_state(df, state):
  return df[df["State"] == state]

def get_states(df):
  return df["State"]

def state_counts():
  return [(state, len(get_by_state(data, state))) for state in get_states(data).unique()]

def gen_viz(df):
  from bokeh.sampledata import us_states, us_counties
  us_states = us_states.data.copy()
  us_counties = us_counties.data.copy()
  res = count_by_state(df).to_dict()
  norm_data = normalized_count(count_by_state(df), state_pops)
  norm_data = norm_data.groupby(["State"])["Death_per_capita"].sum().to_dict()

  del us_states["HI"]
  del us_states["AK"]

  state_xs = [us_states[code]["lons"] for code in us_states]
  state_ys = [us_states[code]["lats"] for code in us_states]

  county_xs=[us_counties[code]["lons"] for code in us_counties if us_counties[code]["state"] not in ["ak", "hi", "pr", "gu", "vi", "mp", "as"]]
  county_ys=[us_counties[code]["lats"] for code in us_counties if us_counties[code]["state"] not in ["ak", "hi", "pr", "gu", "vi", "mp", "as"]]

  colors = ["#F1EEF6", "#D4B9DA", "#C994C7", "#DF65B0", "#DD1C77", "#980043"]

  county_colors = []
  for county_id in us_counties:
    if us_counties[county_id]["state"] in ["ak", "hi", "pr", "gu", "vi", "mp", "as"]:
      continue
    try:
      state_acronym = us_counties[county_id]["state"]
      rate = norm_data[us.states.lookup(state_acronym).name]
      norm_rate = (rate - min(norm_data.values()))/(max(norm_data.values()) - min(norm_data.values()))
      idx = min(int(7*norm_rate), 5)
      county_colors.append(colors[idx])
    except KeyError:
      county_colors.append("black")

  output_file("death-by-cop.html", title="Deaths Caused by Police")

  p = figure(title="Count of Police Killings 2013-15", toolbar_location="left", plot_width=1100, plot_height=700)
  p.patches(county_xs, county_ys, fill_color=county_colors, fill_alpha=0.7, line_color="white", line_width=0.5)
  p.patches(state_xs, state_ys, fill_alpha=0.0, line_color="#884444", line_width=2)

  show(p)

def main():
  gen_viz(data)

main()
