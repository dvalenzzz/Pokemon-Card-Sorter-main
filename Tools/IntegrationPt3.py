import time
from pySerialTransfer import pySerialTransfer as txfer


if __name__ == '__main__':
    try:
        link = txfer.SerialTransfer('COM8')
        
        link.open()
        time.sleep(2) # allow some time for the Arduino to completely reset
        
        while True:
            send_size = 0
            
            ###################################################################
            # Send a list
            ###################################################################
            list_ = [1, 3]
            list_size = link.tx_obj(list_)
            send_size += list_size
            
            ###################################################################
            # Send a string
            ###################################################################
            str_ = 'hello'
            str_size = link.tx_obj(str_, send_size) - send_size
            send_size += str_size
            
            ###################################################################
            # Send a float
            ###################################################################
            float_ = 5.234
            float_size = link.tx_obj(float_, send_size) - send_size
            send_size += float_size
            
            ###################################################################
            # Transmit all the data to send in a single packet
            ###################################################################
            link.send(send_size)
            
            ###################################################################
            # Wait for a response and report any errors while receiving packets
            ###################################################################
            while not link.available():
                # A negative value for status indicates an error
                if link.status.value < 0:
                    if link.status == txfer.Status.CRC_ERROR:
                        print('ERROR: CRC_ERROR')
                    elif link.status == txfer.Status.PAYLOAD_ERROR:
                        print('ERROR: PAYLOAD_ERROR')
                    elif link.status == txfer.Status.STOP_BYTE_ERROR:
                        print('ERROR: STOP_BYTE_ERROR')
                    else:
                        print('ERROR: {}'.format(link.status.name))
            
            ###################################################################
            # Parse response list
            ###################################################################
            rec_list_  = link.rx_obj(obj_type=type(list_),
                                     obj_byte_size=list_size,
                                     list_format='i')
            
            ###################################################################
            # Parse response string
            ###################################################################
            rec_str_   = link.rx_obj(obj_type=type(str_),
                                     obj_byte_size=str_size,
                                     start_pos=list_size)
            
            ###################################################################
            # Parse response float
            ###################################################################
            rec_float_ = link.rx_obj(obj_type=type(float_),
                                     obj_byte_size=float_size,
                                     start_pos=(list_size + str_size))
            
            ###################################################################
            # Display the received data
            ###################################################################
            print('SENT: {} {} {}'.format(list_, str_, float_))
            print('RCVD: {} {} {}'.format(rec_list_, rec_str_, rec_float_))
            print(' ')
    
    except KeyboardInterrupt:
        try:
            link.close()
        except:
            pass
    
    except:
        import traceback
        traceback.print_exc()
        
        try:
            link.close()
        except:
            pass