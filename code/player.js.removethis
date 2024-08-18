var Float = Java.type("java.lang.Float");
var Integer = Java.type("java.lang.Integer");

function tick(entity, utils) {
	// loadPlayerCacheTick(entity, utils);
	openVaultTick(entity, utils);
	return "";
}


var starty = 0;
var num = 0, sf, pos1x, pos1y, pos1z, pos2x, pos2y, pos2z, deg1, deg2;
var pct_i = 1, pct_i_2;
function openVault(entity, utils, args) {
	starty = entity.getY();
	num = Integer.parseInt(args[0]);
	sf = 0;
	pos1x = args[2];
	pos1y = args[3];
	pos1z = args[4];
	deg1 = args[5];
	deg2 = args[6];
	pct_i = Integer.parseInt(args[1]);
	pct_i_2 = Integer.parseInt(args[1]) + 1;

	utils.sendMes("Done.");
}

var lastKill = "", lastUse = "";
function openVaultTick(entity, utils, args) {
	var world = entity.getWorld();
	world = new world_proxy(world);
	var players = world.getPlayers();
	var p_players = [];
	for (var i in players) {
		p_players[i] = new entity_proxy(players[i]);
		if (p_players[i].getName().toString().indexOf("bot_trial_v_") != -1 && lastUse != p_players[i].getName().toString()) {
			lastUse = p_players[i].getName().toString()
			utils.sendMesToPublic("/player " + p_players[i].getName().toString().substr(8, p_players[i].getName().toString().length - 9) + " use continuous");
		}
		if (p_players[i].getY() < starty && p_players[i].getName().toString().indexOf("bot_trial_v_") != -1 && lastKill != p_players[i].getName().toString()) {
			lastKill = p_players[i].getName().toString();
			utils.sendMesToPublic("/player " + p_players[i].getName().toString().substr(8, p_players[i].getName().toString().length - 9) + " kill");
			pct_i_2++;
		}
	}

	if (pct_i < pct_i_2) {
		pct_i++;
		if (pct_i > num) {
			pct_i = 1;
			pct_i_2 = 1;
		}
		utils.sendMesToPublic("/player bot_trial_v_" + (pct_i + sf) + " spawn at " + pos1x + " " + pos1y + " " + pos1z + " facing " + deg1 + " " + deg2);
	}
}

function spawnPlayers(entity, utils, args) {
	var sf = Float.parseFloat(args[1] ? args[1] : 0);
	var x = Float.parseFloat(args[4] ? args[2] : 0);
	var y = Float.parseFloat(args[4] ? args[3] : 0);
	var z = Float.parseFloat(args[4] ? args[4] : 0);
	for (var i = 0; i < args[0]; i++) {
		if (args[4]) {
			utils.sendMesToPublic("/player bot_trial_" + (sf + i) + " spawn at " + x + " " + y + " " + z);
		} else {
			utils.sendMesToPublic("/player bot_trial_" + (sf + i) + " spawn");
		}
	}
}

function killPlayers(entity, utils, args) {
	var sf = Float.parseFloat(args[1] ? args[1] : 0);
	for (var i = 0; i < args[0]; i++) {
		utils.sendMesToPublic("/player bot_trial_" + (sf + i) + " kill");
	}
}


function loadPlayerCache(entity, utils, args) {
	starty = entity.getY();
	num = Integer.parseInt(args[0]);
	sf = Integer.parseInt(args[1]);
	pos1x = args[2];
	pos1y = args[3];
	pos1z = args[4];
	pos2x = args[5];
	pos2y = args[6];
	pos2z = args[7];
	pct_i = 0;

	for (var k = 0; k < 49; k++) {
		utils.sendMesToPublic("/player bot_trial_" + (sf + k) + " spawn at " + pos1x + " " + pos1y + " " + pos1z);
	}
	utils.sendMesToPublic("/player bot_trial_" + (sf + 49) + " spawn at " + pos2x + " " + pos2y + " " + pos2z);

	utils.sendMes("Done.");
}

var lastWaveClean = false, pct_cd = 40;
function loadPlayerCacheTick(entity, utils) {
	if (pct_i > num) return;

	if ((!lastWaveClean) && entity.getY() - starty < 0.5) {
		return;
	}
	if ((!lastWaveClean) && entity.getY() - starty >= 0.5) {
		if (pct_cd > 0) {
			pct_cd--;
			return;
		}
		lastWaveClean = true;
		for (var k = 0; k < 50; k++) {
			utils.sendMesToPublic("/player bot_trial_" + (sf + pct_i + k) + " kill");
		}
		pct_cd = 40;
	}
	if (lastWaveClean && entity.getY() - starty < 0.5) {
		lastWaveClean = false;
		pct_i += 50;
		for (var k = 0; k < 49; k++) {
			utils.sendMesToPublic("/player bot_trial_" + (sf + pct_i + k) + " spawn at " + pos1x + " " + pos1y + " " + pos1z);
		}
		utils.sendMesToPublic("/player bot_trial_" + (sf + pct_i + 49) + " spawn at " + pos2x + " " + pos2y + " " + pos2z);
	}
	// pass
}