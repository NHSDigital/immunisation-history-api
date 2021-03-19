
const request = require("supertest");
const assert = require("chai").assert;
// const expect = require("chai").expect;


describe("app handler tests", function () {
    var server;

    var env;
    before(function () {
        env = process.env;
        let app = require("./app");
        app.setup({LOG_LEVEL: (process.env.NODE_ENV === "test" ? "warn": "debug")});
        server = app.start();

    });

    beforeEach(function () {

    });
    afterEach(function () {

    });
    after(function () {
        process.env = env;
        server.close();

    });

    it("responds to /_ping", (done) => {
        request(server)
            .get("/_ping")
            .expect(200, {
                status: "pass",
                ping: "pong",
                service: "immunisation-history",
                _version: {}
            })
            .expect("Content-Type", /json/, done);
    });

    it("responds to /_status", (done) => {
        request(server)
            .get("/_status")
            .expect(200, {
                status: "pass",
                ping: "pong",
                service: "immunisation-history",
                _version: {}
            })
            .expect("Content-Type", /json/, done);
    });

    it("responds to /hello", (done) => {
        request(server)
            .get("/hello")
            .expect(200, done);
    });
});

