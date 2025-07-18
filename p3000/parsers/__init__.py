from . import Vladimir_parsers, Ivanovo_parsers, pars_manager


start_pars = {
    "Aviator": [Vladimir_parsers.aviator.AviatorParser(exel=True, single=True), "sync"],
    "Glorax": [Vladimir_parsers.glorax.GloraxParser(exel=True, single=True), "async"],
    "Legenda": [Vladimir_parsers.legenda.LegendaParser(exel=True, single=True), "selenium"],
    "Nmarket": [Vladimir_parsers.nmarket.NmarketParser(exel=True, single=True, headless=False), "selenium"],
    "VladimirSK": [Vladimir_parsers.vladimir_sk.VladimirParser(exel=True, single=True), "async"],

    "EuropeyStile": [Ivanovo_parsers.evropey_stile.EuropeyStileParser(exel=True, single=True), "sync"],
    "Olimp": [Ivanovo_parsers.olimp.OlimpParser(exel=True, single=True), "async"],
    "Vidniy": [Ivanovo_parsers.vidniy.VidniyParser(exel=True, single=True), "sync"],
    "CSY": [Ivanovo_parsers.csy.CSYParser(exel=True, single=True), "sync"],
    "DefaultKvartal": [Ivanovo_parsers.default_kvartal.DefaultKvartalParser(exel=True, single=True), "sync"],
    "Levitan": [Ivanovo_parsers.levitan.LevitanParser(exel=True, single=True), "selenium"],
    "KSK_Holding": [Ivanovo_parsers.ksk_holding.KSKHoldingParser(exel=True, single=True), "selenium"],
    "Fenix": [Ivanovo_parsers.fenix.FenixParser(exel=True, single=True, headless=False), "selenium"],
}