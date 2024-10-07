from instrument.tunable_lens.optotune.optotune_icc4c import OptotuneICC4CTunableLens

if __name__ == "__main__":
    etl = OptotuneICC4CTunableLens(id="optotune", port="COM7", channel=0)
    print(etl.temperature_c)
    print(etl.mode)
    etl.mode = "internal"
    print(etl.mode)
    etl.mode = "external"
    print(etl.mode)
    print(etl.log_metadata())
    etl.close()
