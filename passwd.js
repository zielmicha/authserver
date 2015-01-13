var fs = require('fs');
var ldap = require('ldapjs');
var spawn = require('child_process').spawn;
var ArgumentParser = require('argparse').ArgumentParser;
var request = require('request');
var cache = null;
var cachedDate = 0;

var parser = new ArgumentParser({
    version: '0.0.1',
    addHelp: true,
    description: 'LDAP server'
});

parser.addArgument(
    ['-r', '--root-dn'],
    {help: 'Root DN', required: true}
);

parser.addArgument(
    ['-a', '--api-url'],
    {help: 'API url (without trailing slash)', required: true}
)

parser.addArgument(
    ['-t', '--ttl'],
    {help: 'users list cache TTL (0 for unlimited)', defaultValue: 5}
)

parser.addArgument(
    ['-u', '--uid'],
    {help: 'setuid to user'}
)

parser.addArgument(
    ['-g', '--gid'],
    {help: 'setgid to group'}
)

parser.addArgument(
    ['-p', '--port'],
    {help: 'port to listen on', defaultValue: 389}
)

var options = parser.parseArgs();

function loadUserList(req, res, next) {
    if(cache != null && ((new Date).getTime() - cachedDate) < options.ttl * 1000) {
        req.users = cache.users;
        req.groups = cache.groups;
        return next();
    }

    request(
        {
            url: options.api_url + '/users',
            json: true
        },
        function(error, response, body) {
            if(error || response.statusCode != 200)
                return next(new ldap.OperationsError('http error'));

            var data = response.body;

            if(data.status != 'ok')
                return next(new ldap.OperationsError('bad status'));

            req.users = {};
            req.groups = {};

            for(var i = 0; i < data.users.length; i++) {
                var record = data.users[i];

                req.users[record.name] = {
                    dn: 'cn=' + record.name + ', ou=users, ' + options.root_dn,
                    attributes: {
                        cn: record.name,

                        uidnumber: record.uid + '',
                        gidnumber: record.gid + '',
                        uid: record.name,
                        gecos: record.gecos,

                        description: record.gecos,
                        homedirectory: record.home,
                        loginshell: record.shell || '',
                        mail: record.mail,
                        givenName: record.givenName,
                        sn: record.sn,

                        objectclass: ['top', 'posixAccount', 'person']
                    }
                };
            }

            for(var i = 0; i < data.groups.length; i++) {
                var record = data.groups[i];
                req.groups[record.name] = {
                    dn: 'cn=' + record.name + ', ou=groups, ' + options.root_dn,
                    attributes: {
                        cn: record.name,

                        gidnumber: record.gid + '',
                        objectclass: ['top', 'posixGroup'],
                        memberuid: record.members
                    }
                };
            }

            cache = {users: req.users, groups: req.groups};
            cachedDate = (new Date).getTime();

            return next();
        });
}


var pre = [loadUserList];

var server = ldap.createServer();

server.bind('cn=root', function(req, res, next) {
    res.end();
    return next();
});

server.bind('ou=users, ' + options.root_dn, function(req, res, next) {
    var username = req.dn.rdns[0].cn;
    var password = req.credentials;
    request.post(
        {
            url: options.api_url + '/auth',
            form: {name: username, password: password},
            json: true
        },
        function(error, response, body) {
            if(error || response.statusCode != 200)
                return next(new ldap.OperationsError("http error"));

            if(response.body.status != 'ok')
                return next(new ldap.OperationsError("bad response: " + response.status));

            res.end();
            return next();
        }
    )
});

server.add('ou=users, ' + options.root_dn, pre, function(req, res, next) {
  return next(new ldap.OperationsError("not supported"));
});

server.search(options.root_dn, pre, function(req, res, next) {
    Object.keys(req.users).forEach(function(k) {
        if (req.filter.matches(req.users[k].attributes))
            res.send(req.users[k]);
    });

    Object.keys(req.groups).forEach(function(k) {
        if (req.filter.matches(req.groups[k].attributes))
            res.send(req.groups[k]);
    });

  res.end();
  return next();
});

server.listen(options.port, '0.0.0.0', function() {
    try {
        if(options.gid)
            process.setgid(options.gid);
        if(options.uid)
            process.setuid(options.uid);
    } catch(err) {
        console.log('setuid/setgid failed');
        process.exit(1);
    }
    console.log('%s auth LDAP server at: %s', options.api_url, server.url);
});
