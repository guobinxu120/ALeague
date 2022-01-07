# -*- coding: utf-8 -*-

from scrapy import Spider, Request, FormRequest
from collections import OrderedDict
import json, csv, re
from datetime import datetime
from scrapy.http import TextResponse

class aleagueSpider(Spider):
    name = "aleague"
    count = 0
    custom_output = False
    use_selenium = True
    start_url = [
            'https://api.ffa.football/c214/s2020/r13/fixture'
    ]
    datetime_object = None

    def start_requests(self):
        for year in ['2014', '2015', '2016', '2017', '2018', '2019', '2020']:
            for ro in range(50):
                ro_1 = ro + 1
                url = 'https://api.ffa.football/c214/s{}/r{}/fixture'.format(year, str(ro_1))
                yield Request(url, self.parse1, meta={'year': year})            

    def parse1(self, response):
        json_data = json.loads(response.text)
        if json_data['rounds']:
            for rou in json_data['rounds']:
                rou_id = rou['id']
                url = 'https://api.ffa.football/m{}/details'.format(str(rou_id))

                response.meta['rou_id'] = rou_id
                yield Request(url, self.parse, meta=response.meta)

                # break

    def parse(self, response):
        json_data_detail = json.loads(response.text)
        away_team = json_data_detail['away_team']
        home_team = json_data_detail['home_team']
        match_info = json_data_detail['match_info'] 
        venue = json_data_detail['venue'] 

        players_away_team = json_data_detail['away_team']['players']
        players_home_team = json_data_detail['home_team']['players']
        duels_away = 0
        duels_won_away = 0

        duels_home = 0
        duels_won_home = 0

        interceptions_home = 0
        interceptions_away = 0

        shots_on_target_home = 0
        shots_on_target_away = 0

        if players_away_team and ('goals' in players_away_team.keys()):
            for player in players_away_team:
                duels_away += player['duels'] 
                duels_won_away += player['duel_won'] 

                interceptions_away += player['interceptions'] 
                shots_on_target_away += player['shots_on_target'] 

            for player in players_home_team:
                duels_home += player['duels'] 
                duels_home += player['duel_won'] 

                interceptions_home += player['interceptions'] 
                shots_on_target_home += player['shots_on_target'] 

        item = OrderedDict()
        item['url'] = 'https://www.a-league.com.au/match/id/{}#!/stats'.format(str(response.meta['rou_id']))
        item['home_team'] = home_team['name']
        item['away_team'] = away_team['name']

        if ('start_date' in json_data_detail.keys()) and json_data_detail['start_date']:
            start_date = json_data_detail['start_date'].split('+')[0].replace('T', ' ')
            datetime_object = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

            item['date'] = datetime_object.strftime("%m/%d/%Y")        
            item['time'] = datetime_object.strftime("%I:%M %p")  
        else:
            item['date'] = ''       
            item['time'] = ''
        item['attendance'] = match_info['attendance']   
        item['venue'] = venue['name']

        if ('stats' in home_team.keys()) and home_team['stats']:
            item['Home Possession'] = round(home_team['stats']['possession_percentage'], 1)
            item['Away Possession'] = round(away_team['stats']['possession_percentage'], 1)
            item['Home Duels success rate'] = round(home_team['stats']['duel_success_rate'], 1)
            item['Away Duels success rate'] = round(away_team['stats']['duel_success_rate'], 1)

            if duels_home > 0:
                item['Home Aerial duels won'] = round(duels_won_home * 100 / duels_home, 1)
            if duels_away > 0:
                item['Away Aerial duels won'] = round(duels_won_away * 100 / duels_away, 1)

            item['Home Interceptions'] = interceptions_home
            item['Away Interceptions'] = interceptions_away

            item['Home Offsides'] = home_team['stats']['offsides']
            item['Away Offsides'] = away_team['stats']['offsides']

            item['Home Corners'] = home_team['stats']['corners']
            item['Away Corners'] = away_team['stats']['corners']

            item['Home Passes'] = home_team['stats']['total_passes']
            item['Away Passes'] = away_team['stats']['total_passes']

            item['Home Long passes'] = ''
            item['Away Long passes'] = ''

            item['Home Passing accuracy'] = round(home_team['stats']['passing_accuracy'], 1)
            item['Away Passing accuracy'] = round(away_team['stats']['passing_accuracy'], 1)

            item['Home Passing accuracy in opponents half (%)'] = ''
            item['Away Passing accuracy in opponents half (%)'] = ''

            item['Home Crosses'] = home_team['stats']['crosses']
            item['Away Crosses'] = away_team['stats']['crosses']

            item['Home Crossing accuracy'] = home_team['stats']['crossing_accuracy']
            item['Away Crossing accuracy'] = away_team['stats']['crossing_accuracy']

            item['Home Goals'] = home_team['stats']['goals']
            item['Away Goals'] = away_team['stats']['goals']

            item['Home Shots'] = home_team['stats']['shots']
            item['Away Shots'] = away_team['stats']['shots']

            item['Home Shots on target'] = shots_on_target_home
            item['Away Shots on target'] = shots_on_target_away

            item['Home Blocked shots'] = ''
            item['Away Blocked shots'] = ''

            item['Home Shots outside the box'] = ''
            item['Away Shots outside the box'] = ''

            item['Home Shots inside the box'] = ''
            item['Away Shots inside the box'] = ''

            item['Home Shooting accuracy'] = round(home_team['stats']['shooting_accuracy'], 1)
            item['Away Shooting accuracy'] = round(away_team['stats']['shooting_accuracy'], 1)

            item['Home Tackles'] = home_team['stats']['tackles']
            item['Away Tackles'] = away_team['stats']['tackles']

            item['Home Tackles success rate'] = round(home_team['stats']['tackle_success_rate'], 1)
            item['Away Tackles success rate'] = round(away_team['stats']['tackle_success_rate'], 1)

            item['Home Clearances'] = home_team['stats']['clearances']
            item['Away Clearances'] = away_team['stats']['clearances']

            item['Home Fouls conceded'] = home_team['stats']['total_fouls_conceded']
            item['Away Fouls conceded'] = away_team['stats']['total_fouls_conceded']

            item['Home Yellow cards'] = home_team['stats']['yellow_cards']
            item['Away Yellow cards'] = away_team['stats']['yellow_cards']

            item['Home Red cards'] = home_team['stats']['red_cards']
            item['Away Red cards'] = away_team['stats']['red_cards']
        else:
            item['Home Possession'] = ''
            item['Away Possession'] = ''
            item['Home Duels success rate'] = ''
            item['Away Duels success rate'] = ''

            item['Home Aerial duels won'] = ''
            item['Away Aerial duels won'] = ''

            item['Home Interceptions'] = ''
            item['Away Interceptions'] = ''

            item['Home Offsides'] = ''
            item['Away Offsides'] = ''

            item['Home Corners'] = ''
            item['Away Corners'] = ''

            item['Home Corners'] = ''
            item['Away Corners'] = ''

            item['Home Passes'] = ''
            item['Away Passes'] = ''

            item['Home Passing accuracy'] = ''
            item['Away Passing accuracy'] = ''

            item['Home Passing accuracy in opponents half (%)'] = ''
            item['Away Passing accuracy in opponents half (%)'] = ''

            item['Home Crosses'] = ''
            item['Away Crosses'] = ''

            item['Home Crossing accuracy'] = ''
            item['Away Crossing accuracy'] = ''

            item['Home Goals'] = ''
            item['Away Goals'] = ''

            item['Home Shots'] = ''
            item['Away Shots'] = ''

            item['Home Shots on target'] = ''
            item['Away Shots on target'] = ''

            item['Home Blocked shots'] = ''
            item['Away Blocked shots'] = ''

            item['Home Shots outside the box'] = ''
            item['Away Shots outside the box'] = ''

            item['Home Shots inside the box'] = ''
            item['Away Shots inside the box'] = ''

            item['Home Shooting accuracy'] = ''
            item['Away Shooting accuracy'] = ''

            item['Home Tackles'] = ''
            item['Away Tackles'] = ''

            item['Home Tackles success rate'] = ''
            item['Away Tackles success rate'] = ''

            item['Home Clearances'] = ''
            item['Away Clearances'] = ''

            item['Home Fouls conceded'] = ''
            item['Away Fouls conceded'] = ''

            item['Home Yellow cards'] = ''
            item['Away Yellow cards'] = ''

            item['Home Red cards'] = ''
            item['Away Red cards'] = ''
        yield item