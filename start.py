#!/usr/bin/env python3
import os
import argparse
import sys
import json

from test import test_single
from build import build_environment, build_sqlancer_image, build_db_image
from utils import setup_logging


def load_json(path):
    with open(path) as f:
        return json.load(f)


def _build_arg_parser():
    parser = argparse.ArgumentParser(description="AUTO-SQLancer")
    sub = parser.add_subparsers(dest="command", required=True)

    test = sub.add_parser("test", help="Run SQLancer test")
    test.add_argument("--dbms", help="DBMS to test (e.g., mysql, postgres, or 'all')")
    test.add_argument("--config", help="Path to config.json for the DBMS")
    test.add_argument("--dockerfile", help="Path to custom Dockerfile for building DBMS image")
    test.add_argument("--cache", action="store_true", help="Use Docker cache when building image")

    build = sub.add_parser("build", help="Build DBMS or SQLancer Docker image")
    build.add_argument("--dbms", help="DBMS to build (e.g., mysql, postgres, or 'all')")
    build.add_argument("--sqlancer", action="store_true", help="Build SQLancer image only")
    build.add_argument("--cache", action="store_true", help="Use Docker cache when building")

    return parser


def _run_test_command(args, parser, dbms_list, script_log, docker_log, sqlancer_log, run_dir):
    use_cache = args.cache
    if args.dockerfile:
        if not args.config:
            parser.error("Custom DBMS test requires --config")
        cfg = load_json(args.config)
        build_environment(cfg, use_cache, script_log, docker_log, True, args.dockerfile)
        test_single(cfg, script_log, docker_log, sqlancer_log, run_dir, use_cache)

    elif args.dbms == "all":
        for dbms in dbms_list:
            config_path = os.path.join(dbms, "config.json")
            if not os.path.exists(config_path):
                continue
            cfg = load_json(config_path)
            build_environment(cfg, use_cache, script_log, docker_log)
            test_single(cfg, script_log, docker_log, sqlancer_log, run_dir, use_cache)

    elif args.dbms:
        if not args.config:
            parser.error("Single DBMS test requires --config")
        cfg = load_json(args.config)
        build_environment(cfg, use_cache, script_log, docker_log)
        test_single(cfg, script_log, docker_log, sqlancer_log, run_dir, use_cache)

    else:
        parser.error("Must specify either --dbms or --dockerfile")


def _run_build_command(args, parser, dbms_list, script_log, docker_log):
    use_cache = args.cache
    if args.sqlancer:
        build_sqlancer_image(script_log, docker_log, force_rebuild=not use_cache)

    elif args.dbms == "all":
        for dbms in dbms_list:
            config_path = os.path.join(dbms, "config.json")
            if not os.path.exists(config_path):
                continue
            cfg = load_json(config_path)
            build_db_image(cfg, use_cache, script_log, docker_log)

    elif args.dbms:
        config_path = os.path.join(args.dbms, "config.json")
        if not os.path.exists(config_path):
            sys.exit(1)
        cfg = load_json(config_path)
        build_db_image(cfg, use_cache, script_log, docker_log)

    else:
        parser.error("Must specify --dbms or --sqlancer for build command")


def main():
    parser = _build_arg_parser()
    args = parser.parse_args()

    global_cfg = load_json("config.json")
    dbms_list = global_cfg.get("dbms_list", [])

    script_log, docker_log, sqlancer_log, run_dir = setup_logging()
    script_log.info("Log output directory: %s", run_dir)

    if args.command == "test":
        _run_test_command(args, parser, dbms_list, script_log, docker_log, sqlancer_log, run_dir)
    elif args.command == "build":
        _run_build_command(args, parser, dbms_list, script_log, docker_log)


if __name__ == "__main__":
    main()
